import os
import xlsxwriter
import pandas as pd
import re
from openai import OpenAI # type: ignore



chose_model = "gpt-4o"

client = OpenAI(
    base_url='XXXXXXXXXXX',
    api_key= 'XXXXXXXXXXX',
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



def create_prompt(data, example1, example2, example3):
    prompt = f"""{data}
    
    Are there any misconfigurations in the above configuration file? 

    Example 1:
{example1}
    <START>No errors found.<END>

    Example 2:
{example2}
    <START>The `Runtime` value `python1.8` is not a valid runtime. Supported Python runtimes include `python3.8`, `python3.9`, etc.<END>

    Example 3:
{example3}
    <START>The resource type `AWS::Serverless` for `SLN` is incorrect. It should be `AWS::Serverless::Function <END>

    Please summarize the misconfigurations that are absolutely certain. 
    Answer format (You MUST follow this): 
    Detected misconfigurations are written between <START> and <END> tags.
    """
    return prompt


def constraint_method(data, example1, example2, example3):
    
    
    prompt = create_prompt(data, example1, example2, example3)
    # print(prompt)
        
    
    response = client.chat.completions.create(
        model=chose_model,
        messages=[
            {"role": "system", "content": "You are an expert at writing AWS SAM configurations for serverless applications."},
            {"role": "user", "content": prompt},
        ],

        temperature=0,
    )
        
    
    constraint_response = response.choices[0].message.content
    print(constraint_response)
    
    return get_content(constraint_response)
    # print(constraint_responses)
        
    

import time
def main():

    data = []
    
    folder_path = 'TEST'

    output_file = "Output/2-Three_Few_shot-gpt4o-5.csv"




    
    with open("Examples/15-template.yaml", 'r', encoding='utf-8') as file:
        example1 = file.read()
    with open("Examples/32-template.yaml", 'r', encoding='utf-8') as file:
        example2 = file.read()
    with open("Examples/517-sln.yaml", 'r', encoding='utf-8') as file:
        example3 = file.read()


    header_written = False  # 用于跟踪是否已经写入了CSV的表头
    for file_name in os.listdir(folder_path):
        time.sleep(2)
        if file_name.endswith('.yaml'):
            file_path = os.path.join(folder_path, file_name)
            print("---------------------------------------")
            print("----------{}".format(file_path))
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            constraint_response = constraint_method(content, example1, example2, example3)
            data = {
                'Model':chose_model,
                'Configuration':file_name, 
                'Final_responses':constraint_response
                }
            df = pd.DataFrame([data])
            # 追加写入到CSV文件中
            # if not header_written:
            #     df.to_csv(output_file, mode='a', index=False, header=True)
            #     header_written = True
            # else:
            #     df.to_csv(output_file, mode='a', index=False, header=False)
            
            df.to_csv(output_file, mode='a', index=False, header=False)


if __name__ == "__main__":
    main()


