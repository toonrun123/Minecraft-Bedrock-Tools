import requests
import re
import wget
import zipfile
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
    'Accept': 'application/json',
    'Connection': 'keep-alive',
    'Accept-Encoding': 'gzip, deflate, br'
}

IgnoreFile = ["permissions.json","server.properties","Dedicated_Server.txt","allowlist.json","packet-statistics.txt"]

with requests.Session() as session:
    (r := session.get('https://www.minecraft.net/en-us/download/server/bedrock', headers=headers)).raise_for_status()
    html_code = r.text
    search_pattern = r"bedrock-server-(\d+\.\d+\.\d+\.\d+)\.zip"
    version_match = re.search(search_pattern, html_code)
    if version_match:
        version = version_match.group(1)
        print(f'Release Bedrock Server Version: {version}')
        print("Downloading Release Minecraft Bedrock Server...")
        DownloadLink = f'https://minecraft.azureedge.net/bin-linux/bedrock-server-{version}.zip'
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
    else:
        print("Minecraft Bedrock Website not found version string!")