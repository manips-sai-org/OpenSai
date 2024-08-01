# OpenSai

## Install Instructions
Start by installing the dependencies:
```
sh scripts/install_dependencies.sh
```

Then call the setup script that will create a core folder and download and compile all the core sai2 libraries there. It will also install all the python requirements for the interface.
```
sh scripts/install_core_libraries.sh
```

Finally, build the OpenSai_main application (which will be located in the bin folder)
```
sh scripts/build_Opensai.sh
```

## Usage Instructions
You can now launch opensai with the provided script (you can provide as an optional argument a config file name, the file must be in config_folder/main_configs). By default, the application will launch with the single_panda.xml config file if no argument is provided
```
sh scripts/launch.sh
```
To use the ui, open a browser and navigate to localhost:8000 (give it a few seconds for the web server to start)
From the UI, you can load a config file from the config_folder/main_configs folder and interact with the robot controllers

## Updating the core libraries
To pull the latest updates from the core libraries, you can use the provided script that will checkout the master branch of all core libraries and pull the latest changes.
```
sh scripts/update_core_libraries.sh
```
Don't forget to re install them afterwards, and to re build the main application.

## Uninstall instructions
The core libraries are installed for the current OS session user, and the main application is not installed globally. If you want to remove the core libraries installation (to use different versions of those in other applications for example), call the scripts/uninstall_core_libraries.sh script. Be warned that it removes all installation of the sai2 core libraries for the current user, not only this one.



