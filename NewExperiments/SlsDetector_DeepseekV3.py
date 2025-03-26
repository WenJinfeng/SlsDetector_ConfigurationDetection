import os
import xlsxwriter
import pandas as pd
import re
from openai import OpenAI # type: ignore




chose_model = "deepseek/deepseek-chat"



client = OpenAI(
    base_url='XXXXXXX',
    api_key= 'XXXXXX',
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
    prompt = f"""The following is a configuration file:
    {data}
    
    Are there any misconfigurations in the above configuration file? Please consider the following constraints in a category-by-category manner.

    1. Resource Type Constraint: Check whether the resource type is currently supported by AWS SAM. Search the following URL to compare all supported AWS resources listed, noting the letter case. https://docs.aws.amazon.com/serverlessrepo/latest/devguide/list-supported-resources.html.
    2. Entry Constraint: Follow the steps below for a step-by-step check. 
    Step 1: Check whether each configuration entry under each resource type actually exists, paying attention to the accuracy of the name of the configuration entry, including case and singular and plural forms; 
    Step 2: If Events exists, also further check whether the corresponding configuration entry exists under each event source type, and please point out the non-existence of configuration entries;
    Step 3: Check whether the hierarchical level of all configuration entries is correct, and pay attention to the indentation problem.
    3. Value Constraint: Check that the value type, constraints, and supported values of the configuration entry are correct, that the value representation is accurate, and that the value cannot be defined as null.
    4. Entry Dependency: Check if there are dependencies between configuration entries and check that they are used in the correct way, e.g. Ref and that the referenced resource types are correct, and that the relevant required reference definitions are given. Further check which configuration entries are or are not required under the PackageType type.
    5. Value Dependency: Check if there is a dependency (possibly implicit) between the values of configuration entries. Check that the usage is correct and that the relevant required reference definitions are given.

    Please summarize the misconfigurations that are absolutely certain. They are categorized as [Resource Type Errors],[Configuration Entry Errors],[Configuration Entry Value Errors],[Entry Dependency Errors],[Value Dependency Errors] (if present).
    Answer format (You MUST follow this): 
    Detected misconfigurations are written between <START> and <END> tags.
    """
    return prompt

def constraint_method(data):
    # constraint_responses = []
    # final_responses = []  
    
    prompt = create_prompt(data)
        
    
    response = client.chat.completions.create(
        model=chose_model,
        messages=[
            {"role": "system", "content": "You are an expert at writing AWS SAM configurations for serverless applications."},
            {"role": "user", "content": prompt},
        ],

        # for gemini model's input
        # messages=[
        #     {"role": "assistant", "content": "You are an expert at writing AWS SAM configurations for serverless applications."},
        #     {"role": "user", "content": prompt},
        # ],

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

    output_file = "Output/7-DeepseekV3-6.csv"


    header_written = False  
    for file_name in os.listdir(folder_path):
        time.sleep(5)
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


