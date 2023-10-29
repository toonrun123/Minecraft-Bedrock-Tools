import sys
import os
import shutil
import datetime
import zipfile
import json
import io
import requests
import re
import wget
import platform
import json_parser

VERSION = "0.2.0a"

def PrintUsage():
    print(f'Minecraft Bedrock Patcher {VERSION}')
    print(f'Supported: Linux, Windows (untested)')
    print(f'https://github.com/toonrun123/Minecraft-Bedrock-Tools\n')
    print(f'Start Command: python|python3 patcher.py [COMMAND] [ARGS]')
    print(f'  Example Usage: python3 patcher.py import "Bedrock Level"')
    print(f'    init                         // Init required files for patcher (Always run before use another command!)')
    print(f'    install                      // Install Minecraft Bedrock Server')
    print(f'    update                       // Update Bedrock Server to Lastest Version.')
    print(f'    start                        // Start Minecraft Server.')
    print(f'    world-import                 // Import World from BPL/Worlds.')
    print(f'    addons-import [WorldName]    // Import Addons from BPL/Addons.')
    print(f'    worldslist                   // Get Worlds List')
    print(f'    backup-worlds                // Backup World Server.')
if len(sys.argv) < 2:
    PrintUsage()
    sys.exit(1)

MyPath = os.getcwd()
command = sys.argv[1]
arguments = sys.argv[2:]
backup_directory = MyPath+"/WorldsBackup"
os_name = platform.system()

def WriteFile(file_path):
    with open(file_path, "w") as file:
        file.write('[]')

bp_count = 0
rp_count = 0

def clean_json_string(json_str):
    acceptable_chars = ''.join(c for c in json_str if c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789{}[]":,.;- ')
    return acceptable_chars

def process_archive(archive, archive_path, filllist,namemodinstalled,modname):
    for xd in archive.namelist():
        if xd.endswith('.zip') or xd.endswith(".mcpack") or xd.endswith(".mcaddon"):
            nested_archive_data = archive.read(xd)
            nested_archive_path = os.path.join(archive_path, xd)
            nested_archive = zipfile.ZipFile(io.BytesIO(nested_archive_data), 'r')
            process_archive(nested_archive, nested_archive_path, filllist,namemodinstalled,modname)
        elif xd.find("manifest.json") != -1:
            try:
                if xd.find("__MACOSX") == 0:
                    print(f'Ignore __MACOSX {modname}')
                    continue
                raw = clean_json_string(archive.read(xd).decode("utf_8"))
                raw = json.loads(raw)
                filetype = raw["modules"][0]["type"]
                filllist.append({"UID": raw["header"]["uuid"], "VERSION": raw["header"]["version"], "TYPE": filetype})
                direc = "/"
                custom_header = ""
                if filetype == "data" or filetype == "scripts":
                    direc = "/behavior_packs"
                    custom_header = "BP"
                else:
                    direc = "/resource_packs"
                    custom_header = "RP"
                
                archive_name = os.path.splitext(os.path.basename(archive_path))[0]
                output_directory = MyPath + direc
                splspl = xd.split("/")
                newpath = ""
                for i in splspl:
                    if i == splspl[-1]:
                        continue
                    newpath = newpath + i
                parent_dir = os.path.dirname(xd)
                dircheck = xd.split("/")[0]+"/"
                fileheader = ""
                ignore_file = False
                if dircheck == "manifest.json/":
                    fileheader = archive_path.split("/")[-1].split(".")[0]
                    output_directory = output_directory + "/" + fileheader + custom_header
                    ignore_file = True
                for yes in archive.infolist():
                    if yes.filename.startswith(dircheck) or ignore_file == True:
                        archive.extract(yes,output_directory)
                if namemodinstalled.get(modname) != None:
                    continue
                namemodinstalled[modname] = True
                #archive.extractall(member=parent_dir, path=output_directory)
            except Exception as s:
                print(f"Failed Import {modname} :: {s}")
                if namemodinstalled.get(modname) != list:
                    namemodinstalled[modname] = []
                namemodinstalled[modname].append(s)

def printworldlist():
    for i in os.listdir(MyPath+"/worlds/"):
        print('     - "'+i+'"')

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
    'Accept': 'application/json',
    'Connection': 'keep-alive',
    'Accept-Encoding': 'gzip, deflate, br'
}

IgnoreFile = ["permissions.json","server.properties","Dedicated_Server.txt","allowlist.json","packet-statistics.txt"]

def Update():
    with requests.Session() as session:
        (r := session.get('https://www.minecraft.net/en-us/download/server/bedrock', headers=headers)).raise_for_status()
        html_code = r.text
        search_pattern = r"bedrock-server-(\d+\.\d+\.\d+\.\d+)\.zip"
        version_match = re.search(search_pattern, html_code)
        if version_match:
            version = version_match.group(1)
            print(f'Release Bedrock Server Version: {version} ({os_name})')
            print("Downloading Release Minecraft Bedrock Server...")
            binlink = ""
            if os_name == "Linux" or os_name == "Darwin":
                binlink = "bin-linux"
            elif os_name == "Windows":
                binlink = "bin-win"
            elif os_name == "Darwin":
                binlink = "bin-linux"
                print("MacOS Download from bin-Linux.")
            DownloadLink = f'https://minecraft.azureedge.net/{binlink}/bedrock-server-{version}.zip'
            wget.download(DownloadLink,out="release.zip")
            zip_file_path = os.getcwd()+"/release.zip"
            extract_directory = os.getcwd()
            print("\nExtracting...")
            with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
                for file_info in zip_file.infolist():
                    file_path = os.path.join(extract_directory, file_info.filename)
                    if os.path.exists(file_path):
                        if file_info.filename in IgnoreFile:
                            print(f'Ignore {file_info.filename}')
                            continue
                    zip_file.extract(file_info, extract_directory)
            os.remove(zip_file_path)
            print("Removed release.zip")
            print("Success!")
        else:
            print("Minecraft Bedrock Website not found version string!")

if command == "update":
    print("Updating Minecraft Bedrock Server...")
    Update()
elif command == "backup-worlds":
    if not os.path.exists(backup_directory) and not os.path.isdir(backup_directory):
        os.mkdir(backup_directory)
    source_directory = MyPath+"/worlds"
    destination_directory = backup_directory
    original_directory_name = os.path.basename(source_directory)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    new_destination_directory = os.path.join(destination_directory, f"{original_directory_name}_{timestamp}")
    try:
        shutil.copytree(source_directory, new_destination_directory)
        print(f"Directory '{source_directory}' copied to '{new_destination_directory}'.")
    except Exception as e:
        print(f"[ERROR] :: {e}")
elif command == "addons-import":
    if len(arguments) <= 0:
        print("Error Arguements.")
        PrintUsage()
    WorldName = arguments[0]
    WorldDIR = MyPath+"/worlds/"+WorldName
    behpath = WorldDIR + "/world_behavior_packs.json"
    repath = WorldDIR + "/world_resource_packs.json"
    Mods = os.listdir(f'{MyPath}/BPL/Addons')
    if not os.path.exists(WorldDIR):
        print("[ERROR] :: World not found!\n   Worlds List:")
        printworldlist()
        sys.exit()
    if not os.path.exists(behpath):
        WriteFile(behpath)
    if not os.path.exists(repath):
        WriteFile(repath)
    target = []
    namemodinstalled = {}
    for Mod in Mods:
        print(f"Importing {Mod}")
        with zipfile.ZipFile(f'{MyPath}/BPL/Addons/{Mod}', 'r') as archive:
            process_archive(archive, f'{MyPath}/BPL/Addons/{Mod}',target,namemodinstalled,Mod)
    bejsonlinker = []
    rejsonlinker = []
    print("Imported Addons List:")
    for i,v in namemodinstalled.items():
        if v == True:
            print("     "+i)
    print("Failed Imported Addons List:")
    for i,v in namemodinstalled.items():
        if v != True:
            print("     "+i)
            for err in v:
                print(f"           {err}")
    with open(behpath) as json_file:
        datel = json.load(json_file,strict=False)
        for i in target:
            exist = False
            for x in datel:
                if i["UID"] == x["pack_id"]:
                    exist = True
                    break
            if (exist): continue
            if i["TYPE"] != "data": continue 
            bejsonlinker.append({"pack_id": i["UID"],"version": i["VERSION"]})
    with open(repath) as json_file:
        datel = json.load(json_file,strict=False)
        for i in target:
            exist = False
            for x in datel:
                if i["UID"] == x["pack_id"]:
                    exist = True
                    break
            if (exist): continue
            if i["TYPE"] != "resources": continue 
            rejsonlinker.append({"pack_id": i["UID"],"version": i["VERSION"]})
    with open(behpath, "w") as outfile:
        json.dump(bejsonlinker, outfile)
    with open(repath, "w") as outfile:
        json.dump(rejsonlinker, outfile)
    print("Import Adddons Success!")
elif command == "init":
    if not os.path.exists(MyPath+"/BPL"):
        os.mkdir(MyPath+"/BPL")
    if not os.path.exists(MyPath+"/BPL/Addons"):
        os.mkdir(MyPath+"/BPL/Addons")
    if not os.path.exists(MyPath+"/BPL/Worlds"):
        os.mkdir(MyPath+"/BPL/Worlds")
    print("Init!")
    sys.exit()
elif command == "worldslist":
    print("Worlds List:")
    printworldlist()
elif command == "install":
    print("Installing Minecraft Bedrock Server...")
    Update()
elif command == "start":
    if os_name == "Linux":
        os.system("chmod +x bedrock_server")
        os.system('LD_LIBRARY_PATH=. ./bedrock_server')
    elif os_name == "Windows":
        os.system("bedrock_server.exe")
    elif os_name == "Darwin":
        print("i dont know how to")
elif command == "world-import":
    WorldsList = os.listdir(f'{MyPath}/BPL/Worlds')
    if len(WorldsList) <= 0:
        print("Worlds List not found, Please add any *.mcworld into BPL/Worlds!")
    print(f'What world do you want to import?')
    c = 1
    for i in WorldsList:
        goodstring = clean_json_string(i.split('.mcworld')[0])
        print(f"       {c}. {goodstring}")
        c+=1
    result = int(input(f"Choose Between 1-{c-1} or 0 for Cancel: "))
    if result == 0:
        print("Operation Cancelled.")
        sys.exit()
    with zipfile.ZipFile(f'{MyPath}/BPL/Worlds/{WorldsList[result-1]}', 'r') as archive:
        strfilted = clean_json_string(WorldsList[result-1].split('.mcworld')[0])
        opfolder = MyPath+"/worlds/"+strfilted
        if not os.path.exists(opfolder):
            os.mkdir(opfolder)
        archive.extractall(opfolder)
        print(f'Imported {strfilted}\n     - Edit server.properties level-name to "{strfilted}" to apply world.')
else:
    print("Unknown Command.")