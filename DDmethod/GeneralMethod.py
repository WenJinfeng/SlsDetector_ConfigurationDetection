
# Core foundation of uniform representation trasformation

def transforRepPattern(flat_config):
    TypeMappingName = {}
    flat_config_key_new = []
    flat_config_value_new = []

    # specialNotType = ["EndpointConfiguration", "DeploymentPreference"]

    for key_i in flat_config.keys():
        key_i_tmp = key_i.split(".")
        rootname = key_i_tmp[0]
        if (key_i_tmp[-1] == "Type") and (key_i_tmp[-2] != "Properties"):
           
           definedType = flat_config[key_i]
           if definedType not in TypeMappingName.keys():
               TypeMappingName[definedType] = []
               
           definedName = key_i_tmp[-2]
           index = key_i_tmp.index(definedName)
           nameAndindex = [definedName, index, rootname]

           TypeMappingName[definedType].append(nameAndindex)
    for key_i in flat_config.keys():
        key_i_tmp = key_i.split(".")
        rootname = key_i_tmp[0]
        
        if rootname != "Mappings":

            for fieldindex_i in range(len(key_i_tmp)):
                field_i = key_i_tmp[fieldindex_i]
                for Type_i in TypeMappingName.keys():
                    for k in TypeMappingName[Type_i]:
                        if field_i == k[0] and fieldindex_i == k[1] and rootname == k[2]:
                            key_i_tmp[fieldindex_i] = "PH{}".format(Type_i)
        
            if rootname =="Outputs":
                key_i_tmp[1] = "PHOutputLogicID"
            if rootname == "Conditions":
                key_i_tmp[1] = "PHConditionLogicID"
        
            flat_config_key_new.append(".".join(key_i_tmp))
            flat_config_value_new.append(flat_config[key_i])
    
    return flat_config_key_new, flat_config_value_new





import yaml
import os


# learn configuration values for the configuration entry
def findElementValue():
    directoryPath = "Dataset"
    # directoryPath_office = "../Dataset/configuration files-office"

    total_flat_config = uniRepAll(directoryPath)
    # total_flat_config_office = uniRepAll(directoryPath_office)
    
    # total_flat_config.extend(total_flat_config_office)

    
    keyMapValue = {}
    for file_i in total_flat_config:
        flat_config = file_i
        flat_config_key_new, flat_config_value_new = transforRepPattern(flat_config)
        # print(flat_config_value_new)
        for index in range(len(flat_config_key_new)):
            if flat_config_key_new[index] not in keyMapValue:
                keyMapValue[flat_config_key_new[index]] = []
    
            keyMapValue[flat_config_key_new[index]].append(flat_config_value_new[index])

    
 
    print("update cnfiguraiton entry values")

    return keyMapValue


# find configuration entry values from a specific dataset
def findElementValueFromADataset(directoryPath):

    total_flat_config = uniRepAll(directoryPath)

    keyMapValue = {}
    for file_i in total_flat_config:
        flat_config = file_i
        flat_config_key_new, flat_config_value_new = transforRepPattern(flat_config)

        for index in range(len(flat_config_key_new)):
            if flat_config_key_new[index] not in keyMapValue:
                keyMapValue[flat_config_key_new[index]] = []
            keyMapValue[flat_config_key_new[index]].append(flat_config_value_new[index])

    
    filter_keyMapValue = {}
    specialString = [".Variables", ".Variables.", "Properties.Parameters", "Description", "description", ".StageName", ".Name", ".Author", "ApplicationId", ".Value", "TableName", "Parameters.PHString.AllowedValues"]

    for key in keyMapValue.keys():
        flag = checkListEntryInValue(key, specialString)
        if flag == 0:  
            value_filter = removeRepeat(keyMapValue[key])
            filter_keyMapValue[key] = value_filter


    return filter_keyMapValue


def uniRepAll(directoryPath):
   
    filenames = readfiles(directoryPath)

    total_flat_config = []
    for file_i in filenames:
        # print(file_i)
        flat_config = uniRep(file_i)
        for checkKey in flat_config.keys():
            if checkKey == "Transform":
                total_flat_config.append(flat_config)

    return total_flat_config





# Whether the string of any each item in the configuration entry list is contained in the string of value
# # A return value of 0 means none are present. A value greater than 0 indicates presence.
def checkListEntryInValue(value, checklist):
    checkflag = 0
    for k in checklist:
        if k not in value:
            checkflag = checkflag + 0
        else:
            checkflag = checkflag + 1
    return checkflag

#De-duplication for lists containing elements of various types
def removeRepeat(original_list):
    unique_list = []
    for item in original_list:
        if item not in unique_list:
            unique_list.append(item)
    return unique_list


def readfiles(directoryPath):

    filenames = []
    for root, dirs, files in os.walk(directoryPath):
        for name in files:
            if name.endswith('.yaml') or name.endswith('.yml'):
                filename = directoryPath+"/"+name
                filenames.append(filename)

    return filenames



def uniRep(config_path):
    config = parseyaml(config_path)
    flat_config = flatten_dict(config)
    return flat_config



def ref_constructor(loader, node):
    value = loader.construct_scalar(node)
    return {'Ref': value}


def getatt_constructor(loader, node):
    if isinstance(node, yaml.ScalarNode):
        value = loader.construct_scalar(node)
    elif isinstance(node, yaml.SequenceNode):
        value = loader.construct_sequence(node, deep=True)
    return {'Fn::GetAtt': value}



def sub_constructor(loader, node):
    if isinstance(node, yaml.ScalarNode):
        value = loader.construct_scalar(node)
    elif isinstance(node, yaml.SequenceNode):
        value = loader.construct_sequence(node, deep=True)
    return {'Fn::Sub': value}

def join_constructor(loader, node):
    value = loader.construct_sequence(node, deep=True)
    return {'Fn::Join': value}

def select_constructor(loader, node):
    value = loader.construct_sequence(node, deep=True)
    return {'Fn::Select': value}


def split_constructor(loader, node):
    value = loader.construct_sequence(node, deep=True)
    return {'Fn::Split': value}

def import_value_constructor(loader, node):
    value = loader.construct_scalar(node)
    return {'Fn::ImportValue': value}
    


def find_in_map_constructor(loader, node):
    value = loader.construct_sequence(node, deep=True)
    return {'Fn::FindInMap': value}


def equals_constructor(loader, node):
    value = loader.construct_sequence(node)
    return {'Fn::Equals': value}

def not_constructor(loader, node):
    value = loader.construct_sequence(node)
    return {'Fn::Not': value}

def if_constructor(loader, node):
    value = loader.construct_sequence(node, deep=True)
    return {'Fn::If': value}

def and_constructor(loader, node):
    value = loader.construct_sequence(node, deep=True)
    return {'Fn::And': value}

def condition_constructor(loader, node):
    value = loader.construct_scalar(node)
    return {'Fn::Condition': value}

def or_constructor(loader, node):
    value = loader.construct_sequence(node, deep=True)
    return {'Fn::Or': value}


def parseyaml(yamlPath):
    
    yaml.add_constructor("!Ref", ref_constructor)
    yaml.add_constructor('!GetAtt', getatt_constructor)
    yaml.add_constructor('!Sub', sub_constructor)
    yaml.add_constructor('!Join', join_constructor)
    yaml.add_constructor('!Select', select_constructor)
    yaml.add_constructor('!Split', split_constructor)
    yaml.add_constructor('!FindInMap', find_in_map_constructor)
    yaml.add_constructor('!Equals', equals_constructor)
    yaml.add_constructor('!Not', not_constructor)
    yaml.add_constructor('!If', if_constructor)
    yaml.add_constructor('!And', and_constructor)
    yaml.add_constructor('!Condition', condition_constructor)
    yaml.add_constructor('!Or', or_constructor)
    yaml.add_constructor('!ImportValue', import_value_constructor)

    open_file = open(yamlPath, 'r', encoding='utf-8')
    result = open_file.read()
    file_dict = yaml.load(result, Loader=yaml.FullLoader)
    
    
    file_dict["id"] = yamlPath
    

    with open(yamlPath, 'r') as file:
        try:
            config = yaml.load(file, Loader=yaml.FullLoader)
            # config["id"] = yamlPath
            return config
        except yaml.YAMLError as e:
            print(e)
            return None

    


def flatten_dict(data, prefix=''):
    flat_dict = {}
    for key, value in data.items():
        new_key = prefix + '.' + key if prefix else key
        if isinstance(value, dict):
            flat_dict.update(flatten_dict(value, new_key))
        else:
            flat_dict[new_key] = value
    return flat_dict


