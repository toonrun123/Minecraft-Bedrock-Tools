
## Bedrock Tools
This tool let you import addons / update server / install server by one command.

## Features
 #### Quick Start Server
    Only one command!
 #### Quick Import Addons
    Install addons with one command (Please look Install Addons Topic for details.)
 #### Update/Install
    Let you update/install server instantly (Please look Note Topic for details)
 #### Backup
    Copy your worlds into backup folder.
## Getting Start
```
 0.pip install datetime requests wget json_parser
 1.clone this repos into your server directory
 2.copy patcher.py into your server directory
 3.run python|python3 update.py init
```
## Usage
  ```
    init                         // Init required files for patcher (Always run before use another command!)
    install                      // Install Minecraft Bedrock Server
    update                       // Update Bedrock Server to Lastest Version.
    start                        // Start Minecraft Server.
    world-import                 // Import World from BPL/Worlds.
    addons-import [WorldName]    // Import Addons from BPL/Addons.
    worldslist                   // Get Worlds List
    backup-worlds                // Backup World Server.
```
## Install Addons
```
1. pre-create world (Recommend to Toggle Experiment Mode) 
   OR you can edit level.dat file, please look Troubleshooting topic.
2. download addons (*.mcaddons/mcpacks/etc) into BPL/Addons
3. run addons-import command
4. restart server
```
## Troubleshooting
 ```
 Import Addons Already but it didn't work
    -Addons may not in directory. (Put in Server_Directory/BPL/Addons)
    -Addons Require Experiment Mode.
    -That Addon didn't support current version.

 How do i set to Experiment Mode (2 ways)
    1.(Recommend) Import level.dat from Pre-settings World.
    2.(Not Recommend) (Backup World Recommend) Patching level.dat by using offroaders123.github.io/Dovetail Website.
    find experiments then edit like this (1.20.40.01)
        {
            cameras: 1b,
            data_driven_biomes: 1b,
            data_driven_items: 1b,
            experimental_molang_features: 1b,
            experiments_ever_used: 1b,
            gametest: 1b,
            saved_with_toggled_experiments: 1b,
            upcoming_creator_features: 1b
        }
    then save and replace your old
 ```
## Note
 - permissions.json 
 - server.properties 
 - Dedicated_Server.txt 
 - allowlist.json 
 - packet-statistics.txt
These FIles will **not getting override** update/install Server.
