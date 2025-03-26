import os
import xlsxwriter
import pandas as pd
import re
from openai import OpenAI # type: ignore




chose_model = "deepseek-chat"



client = OpenAI(
    base_url='XXXXXXXX',
    api_key= 'XXXXXXXX',
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

# baseline1 simple prompt
def create_prompt(data):
    prompt = f"""{data}

    Are there any configuration errors in the above configuration?

    Answer format (You MUST follow this):
    Detected errors are written between <START> and <END> tags.
    """
    return prompt

def constraint_method(data):
    
    
    prompt = create_prompt(data)
        
    
    response = client.chat.completions.create(
        model=chose_model,
        messages=[
            {"role": "system", "content": ""},
            {"role": "user", "content": prompt},
        ],

        
        temperature=0,
    )
        
    
    constraint_response = response.choices[0].message.content
    print(constraint_response)
    
    return get_content(constraint_response)
   


import time
def main():

    data = []
    
    folder_path = 'TEST'

    output_file = "Output/8-DeepseekV3_Simple-1.csv"


    header_written = False 
    for file_name in os.listdir(folder_path):
        time.sleep(3)
        if file_name.endswith('.yaml'):
            file_path = os.path.join(folder_path, file_name)
            print("---------------------------------------")
            print("----------{}".format(file_path))
            with open(file_path, 'r', encoding='utf-8') as file:
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


