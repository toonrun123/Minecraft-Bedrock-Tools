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

VERSION = "0.1.0a"

def PrintUsage():
    print(f'Minecraft Bedrock Patcher {VERSION}')
    print(f'Supported: Linux, Windows (untested)')
    print(f'https://github.com/toonrun123/Minecraft-Bedrock-Tools\n')
    print(f'Start Command: python|python3 patcher.py [COMMAND] [ARGS]')
    print(f'  Example Usage: python3 patcher.py import "Bedrock Level"')
    print(f'    init                         // Init required files for patcher (Always run before use another command!)')
    print(f'    install                      // Install Minecraft Bedrock Server')
    print(f'    update                       // Update Bedrock Server to Lastest Version.')
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

def process_archive(archive, archive_path, filllist):
    for xd in archive.namelist():
        if xd.endswith('.zip'):
            nested_archive_data = archive.read(xd)
            nested_archive_path = os.path.join(archive_path, xd)
            nested_archive = zipfile.ZipFile(io.BytesIO(nested_archive_data), 'r')
            process_archive(nested_archive, nested_archive_path, filllist)
        elif xd.find("manifest.json") != -1:
            raw = archive.read(xd).decode("utf-8")
            raw = json.loads(raw, strict=False)
            filetype = raw["modules"][0]["type"]
            filllist.append({"UID": raw["header"]["uuid"], "VERSION": raw["header"]["version"], "TYPE": filetype})
            direc = "/"
            if filetype == "data":
                direc = "/behavior_packs"
            else:
                direc = "/resource_packs"
            
            archive_name = os.path.splitext(os.path.basename(archive_path))[0]
            output_directory = os.path.join(MyPath + direc, archive_name)
            os.makedirs(output_directory, exist_ok=True)
            splspl = xd.split("/")
            newpath = ""
            for i in splspl:
                if i == splspl[-1]:
                    continue
                newpath = newpath + i
            parent_dir = os.path.dirname(xd)
            for yes in archive.namelist():
                archive.extract(xd,output_directory)
            #archive.extractall(member=parent_dir, path=output_directory)

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
            if os_name == "Linux":
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
    WorldName = arguments[0]
    if WorldName == None:
        print("yes")
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
    for Mod in Mods:
        print(f'Installing {Mod}')
        with zipfile.ZipFile(f'{MyPath}/BPL/Addons/{Mod}', 'r') as archive:
            process_archive(archive, f'{MyPath}/BPL/Addons/{Mod}',target)
    bejsonlinker = []
    rejsonlinker = []
    with open(behpath) as json_file:
        datel = json.load(json_file)
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
        datel = json.load(json_file)
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
    print("Init!")
    sys.exit()
elif command == "worldslist":
    print("Worlds List:")
    printworldlist()
elif command == "install":
    print("Installing Minecraft Bedrock Server...")
    Update()
else:
    print("Unknown Command.")