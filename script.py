import yaml
import json
import logging
import re
import tarfile
import subprocess
import os
def create_json_from_yaml(yaml_file,json_file): 
    """ take yaml file name, which assumed it be in same directory of the script then open it and convert to dictionary, then convert dictionary to
    json file format then save it in jsonFile name, and return that dictionary"""
    try:
        with open(yaml_file) as input_file: # read yaml file AND CONVERT IT TO DICTIONARY AND JSON STRING
            app_manifist=yaml.load(input_file, Loader=yaml.FullLoader)
            json_string=json.dumps(app_manifist,indent=4) #convert to json string with indent=4
            logging.info("FILE CONVERTED TO JSON SUCCESSFULLY")
                        
    except (FileNotFoundError,FileExistsError) as error: #file doesn't exist
        logging.warning("yaml file is not exist or damaged")
        return None
    
    except yaml.scanner.ScannerError as error: # yaml file syntax error
        logging.warning("wrong yaml format")
        return None

  
    with open(json_file,"w") as output_file:
        output_file.write(json_string)
        logging.info("JSON FILE CREATED SUCCESSFULLY")
    return app_manifist
   

def create_release_notes(yaml_file, realease_notes_file, application_name):
    """ take yaml file file and create dictionary from it then create it in release note"""
    try:
        with open(yaml_file) as input_file: # read yaml file AND CONVERT IT INTO DICTIONARY
            release_dict=yaml.load(input_file, Loader=yaml.FullLoader)
            logging.info("FILE CONVERTED TO DICTIONARY SUCCESSFULLY")
            
                        
    except (FileNotFoundError,FileExistsError) as error: #file doesn't exist
        logging.warning("yaml file is not exist or damaged")
        return None
    
    except yaml.scanner.ScannerError as error: # yaml file syntax error
        logging.warning("wrong yaml format")
        return None
    

    with open(realease_notes_file,"w") as output_file :# create release note and write on it
        for key,value in release_dict.items():
            output_file.write(f"{key}: \n")
            if type(value) == dict:
                for key2,value2 in value.items():
                    output_file.write(f"  {key2}: {value2} \n")
            else:
                for value2 in value:
                    output_file.write(f"  {value2} \n")
            output_file.write("\n")
        logging.info("RELEASE NOTES FILE CREATED SUCCESSFULLY") 
    return release_dict

def download_package(name,arch):
    
    command=f"yumdownloader -x \*i686 --archlist={arch} {name}"
    
    try:
        p=subprocess.run(command,shell=True)
        return True
    except :
        return False


    

###############APPLICATION NAME AND ARCH#############################
APPLICATION_NAME="CVM_PE_GI-7.7r1.6.1-20200303"
APPLICATION_ARCH="x86_64"
#####################################################################

################ INPUT AND OUTPUT FILES##############################
YAML_TO_JSON_FILE="toJson.yml"
YAML_TO_RELEASE_NOTES="toReleaseNote.yml"
JSON_OUTPUT_FILE="CVM_RPM_LIST_MANIFEST.json"
RELEASE_NOTES_OUTPUT_FILE=f"{APPLICATION_NAME}-{APPLICATION_ARCH}.release_notes"
files_list=[RELEASE_NOTES_OUTPUT_FILE,JSON_OUTPUT_FILE] #rmps will be add later
#####################################################################

 
create_json_from_yaml(YAML_TO_JSON_FILE,JSON_OUTPUT_FILE) #create json file from yaml
create_release_notes(YAML_TO_RELEASE_NOTES,RELEASE_NOTES_OUTPUT_FILE,APPLICATION_NAME) # create application releasenotes
try:
    with open(JSON_OUTPUT_FILE) as file: # read yaml file AND CONVERT IT INTO DICTIONARY
        manifist=json.load(file)
        pattern=re.compile(r"([a-zA-z0-9\.\-\_]+)-([a-z0-9\._]+).([A-Za-z0-9_]+).rpm$")
        pattern_arch=re.compile(r".([A-Za-z0-9_]+).rpm$")
        for cesa_list in manifist["CESA_list"]:
            
            package_name=pattern.search(cesa_list["RPM_list"][0]["rpm_pkg"]).groups()[0]
            arch=pattern_arch.search(cesa_list["RPM_list"][0]["rpm_pkg"]).groups()[0]
            download_package(package_name,arch)        
                   
except (FileNotFoundError,FileExistsError) as error: #file doesn't exist
    logging.warning("yaml file is not exist or damaged")
    
    
except json.decoder.JSONDecodeError as error: # yaml file syntax error
    logging.warning("wrong json format")
    
################ZIP rpms,json,and released notes##########################
files_in_path=os.listdir()
pattern_rpm=re.compile(r"(^[a-zA-Z0-9\-\._]+.rpm)")
rpm_files=[]
for item in os.listdir():
    
    if pattern_rpm.search(item):
        rpm_files.append(pattern_rpm.search(item).groups()[0])

files_list.extend(rpm_files)        
tar = tarfile.open(f"{APPLICATION_NAME}-{APPLICATION_ARCH}.tar.gz", "w:gz")
for name in files_list:
    tar.add(name)
tar.close()

#note: add logger after each step

