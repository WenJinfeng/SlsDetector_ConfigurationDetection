import os
import pandas as pd
import re
from openai import OpenAI # type: ignore


chose_model = "gpt-4o"
# chose_model = "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo" 
# chose_model = "gemini-1.5-pro" 


client = OpenAI(
    base_url='XX',
    api_key='XXX',
)

def get_content(text):
    
    pattern = r'(<START>.*?<END>)'
    result = re.findall(pattern, text, re.DOTALL)
    

    if result:
        return result
    else:
        
        return [text]

def get_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


def create_prompt(data):
    prompt = f"""{data}

    Are there any configuration errors in the above configuration?

    Please list the misconfigurations that are absolutely certain.
    Answer format (You MUST follow this):
    Detected errors are written between <START> and <END> tags.
    """
    return prompt

def constraint_method(data):
    
    prompt = create_prompt(data)
        
    
    response = client.chat.completions.create(
        model=chose_model,
        # for gpt4o and llama
        messages=[
            {"role": "system", "content": ""},
            {"role": "user", "content": prompt},
        ],

        # for gemini
        # messages=[
        #     {"role": "user", "content": prompt},
        # ],

        temperature=0,
    )
        
   
    constraint_response = response.choices[0].message.content
    print(constraint_response)
    
    return get_content(constraint_response)
 

def main():

    data = []
    file_name = 'TEST/XX.yaml'
    output_file = "Output/output-baseline2-gpt4o.csv"

    
    with open(file_name, 'r', encoding='utf-8') as file:
        content = file.read()
    constraint_response = constraint_method(content)
    data = {
        'Model':chose_model,
        'Configuration':file_name, 
        'Final_responses':constraint_response
        }
    df = pd.DataFrame([data])

    df.to_csv(output_file, mode='a', index=False, header=False)


if __name__ == "__main__":
    main()


