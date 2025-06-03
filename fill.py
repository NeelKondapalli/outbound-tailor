import pandas as pd
from prompts import prompt2 as prompt
import anthropic
from concurrent.futures import ThreadPoolExecutor, as_completed

def run_personalization(input_path, output_path, anthropic_key, linkup_key):
    df = pd.read_csv(input_path, header=None)
    new_df = pd.DataFrame(columns=['Company Name', 'Domain', 'Message'])
    new_df['Company Name'] = df.iloc[:, 0]
    new_df['Domain'] = df.iloc[:, 1]

    def task(row):
        company_name = row['Company Name']
        domain = row['Domain']
        message = generate_message(company_name, domain, anthropic_key, linkup_key)
        return message

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(task, row): idx for idx, row in new_df.iterrows()}
        for future in as_completed(futures):
            idx = futures[future]
            try:
                message = future.result()
            except Exception as e:
                message = f"Error: {e}"

            new_df.at[idx, 'Message'] = message

    new_df.to_excel(output_path, index=False)
    return output_path

def generate_message(company_name, domain, anthropic_key, linkup_key):
    
    client = anthropic.Anthropic(api_key=anthropic_key)
    response = client.beta.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": f"COMPANY NAME: {company_name}, DOMAIN: {domain} \n\n\n{prompt}"
        }],
        mcp_servers=[{
            "type": "url",
            "url": f"https://mcp.linkup.so/sse?apiKey={linkup_key}",
            "name": "Internet Company Search",
        }],
        betas=["mcp-client-2025-04-04"]
    )

    text_blocks = [block.text for block in response.content if hasattr(block, 'text')]
    print(text_blocks)
    return ''.join(text_blocks)

    # return f"Hello, I'm reaching out to you because I'm interested in {company_name}. I'm a software engineer and I'm looking for a new challenge. I'm interested in your company because it's a great fit for my skills."