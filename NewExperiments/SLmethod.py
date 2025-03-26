import os
import xlsxwriter
import pandas as pd
import re
from openai import OpenAI # type: ignore



chose_model = "gpt-4o"
# chose_model = "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo" 
# chose_model = "gemini-1.5-pro"



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



def create_prompt_ResourceType(data):
    prompt = f"""{data}

    Are there any misconfigurations related to resource type in the above configuration file?

    Resource Type Constraint: Check whether the resource type is currently supported by AWS SAM. Search the following URL to compare all supported AWS resources listed, noting the letter case. https://docs.aws.amazon.com/serverlessrepo/latest/devguide/list-supported-resources.html.
    
    Please summarize the misconfigurations that are absolutely certain. They are categorized as [Resource Type Errors] (if present).
    Answer format (You MUST follow this) (limit to 100 words): 
    Detected misconfigurations are written between <START> and <END> tags.
    """
    return prompt


def create_prompt_ConfigurationEntry(data):
    prompt = f"""{data}

    Are there any misconfigurations related to configuration entry in the above configuration file?

    Entry Constraint: Follow the steps below for a step-by-step check. 
    Step 1: Check whether each configuration entry under each resource type actually exists, paying attention to the accuracy of the name of the configuration entry, including case and singular and plural forms; 
    Step 2: If Events exists, also further check whether the corresponding configuration entry exists under each event source type, and please point out the non-existence of configuration entries;
    Step 3: Check whether the hierarchical level of all configuration entries is correct, and pay attention to the indentation problem.
    
    Please summarize the misconfigurations that are absolutely certain. They are categorized as [Configuration Entry Errors] (if present).
    Answer format (You MUST follow this) (limit to 100 words): 
    Detected misconfigurations are written between <START> and <END> tags.
    """
    return prompt


def create_prompt_ConfigurationEntryValue(data):
    prompt = f"""{data}

    Are there any misconfigurations related to configuration entry value in the above configuration file?

    Value Constraint: Check that the value type, constraints, and supported values of the configuration entry are correct, that the value representation is accurate, and that the value cannot be defined as null.

    Please summarize the misconfigurations that are absolutely certain. They are categorized as [Configuration Entry Value Errors] (if present).
    Answer format (You MUST follow this) (limit to 100 words): 
    Detected misconfigurations are written between <START> and <END> tags.
    """
    return prompt


def create_prompt_EntryDependency(data):
    prompt = f"""{data}

    Are there any misconfigurations related to entry dependency in the above configuration file?

    Entry Dependency Constraint: Check if there are dependencies between configuration entries and check that they are used in the correct way, e.g. Ref and that the referenced resource types are correct, and that the relevant required reference definitions are given. Further check which configuration entries are or are not required under the PackageType type.
    
    Please summarize the misconfigurations that are absolutely certain. They are categorized as [Entry Dependency Errors] (if present).
    Answer format (You MUST follow this) (limit to 100 words): 
    Detected misconfigurations are written between <START> and <END> tags.
    """
    return prompt


def create_prompt_ValueDependency(data):
    prompt = f"""{data}

    Are there any misconfigurations related to value dependency in the above configuration file?

    Value Dependency Constraint: Check if there is a dependency (possibly implicit) between the values of configuration entries. Check that the usage is correct and that the relevant required reference definitions are given.

    Please summarize the misconfigurations that are absolutely certain. They are categorized as [Value Dependency Errors] (if present).
    Answer format (You MUST follow this) (limit to 100 words): 
    Detected misconfigurations are written between <START> and <END> tags.
    """
    return prompt

def constraint_method(data):
    
    prompt_resourcetype = create_prompt_ResourceType(data)
    prompt_configurationentry = create_prompt_ConfigurationEntry(data)
    prompt_configurationentryvalue = create_prompt_ConfigurationEntryValue(data)
    prompt_entrydependency = create_prompt_EntryDependency(data)
    prompt_valuedependency = create_prompt_ValueDependency(data)
        
    
    response1 = client.chat.completions.create(
        model=chose_model,
        messages=[
            {"role": "system", "content": "You are an expert at writing AWS SAM configurations for serverless applications."},
            {"role": "user", "content": prompt_resourcetype},
        ],

        temperature=0,
    )
        
    
    constraint_response1 = response1.choices[0].message.content
    print(constraint_response1)
    content1 =  get_content(constraint_response1)[0]

    response2 = client.chat.completions.create(
        model=chose_model,
        messages=[
            {"role": "system",
             "content": "You are an expert at writing AWS SAM configurations for serverless applications."},
            {"role": "user", "content": prompt_configurationentry},
        ],

        temperature=0,
    )

    
    constraint_response2 = response2.choices[0].message.content
    print(constraint_response2)
    content2 = get_content(constraint_response2)[0]

    response3 = client.chat.completions.create(
        model=chose_model,
        messages=[
            {"role": "system",
             "content": "You are an expert at writing AWS SAM configurations for serverless applications."},
            {"role": "user", "content": prompt_configurationentryvalue},
        ],

        temperature=0,
    )

   
    constraint_response3 = response3.choices[0].message.content
    print(constraint_response3)
    content3 = get_content(constraint_response3)[0]

    response4 = client.chat.completions.create(
        model=chose_model,
        messages=[
            {"role": "system",
             "content": "You are an expert at writing AWS SAM configurations for serverless applications."},
            {"role": "user", "content": prompt_entrydependency},
        ],

        temperature=0,
    )

    constraint_response4 = response4.choices[0].message.content
    print(constraint_response4)
    # constraint_responses.append(constraint_response)
    # constraint_responses.append(get_content(constraint_response))
    content4 = get_content(constraint_response4)[0]

    response5 = client.chat.completions.create(
        model=chose_model,
        messages=[
            {"role": "system",
             "content": "You are an expert at writing AWS SAM configurations for serverless applications."},
            {"role": "user", "content": prompt_valuedependency},
        ],

        temperature=0,
    )


    constraint_response5 = response5.choices[0].message.content
    print(constraint_response5)
    # constraint_responses.append(constraint_response)
    # constraint_responses.append(get_content(constraint_response))
    content5 = get_content(constraint_response5)[0]

    content = content1 + '\n' + content2 + '\n' + content3 + '\n' + content4 + '\n' + content5

    return [content]




    

import time
def main():

    data = []
    
    folder_path = 'TEST'

    output_file = "Output/1-Separated-gpt4o-5.csv"



    header_written = False  
    for file_name in os.listdir(folder_path):
        time.sleep(4)
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


