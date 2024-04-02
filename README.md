# OpenSai

## Install Instructions
Start by installing the dependencies (not tested yet):
```
sh install_dependencies.sh
```

Then call the setup script that will create a core folder and download and compile all the core sai2 libraries there, and finally compile the OpenSai_main application (which will be located in the bin folder)
```
sh setup.sh
```

If you want to use the UI interface, you will need to install the interface dependencies as well
```
pip install -r core/sai2-interfaces/interface/requirements.txt
```

## Usage Instructions
You can now launch opensai with the provided script (you can provide as an optional argument a config file name, the file must be in config_folder/main_configs)
```
sh launch.sh
```
And if you want to use the ui, you can open a browser and navigate to localhost:8000 (give it a few seconds for the web server to start)
From the UI, you can load a config file from the config_folder/main_configs folder and interact with the robot controllers

## Uninstall instructions
The core libraries are installed for the current OS user, and the main application is not installed globally. If you want to remove the core libraries install (to use different versions of those in other applications for example), call the uninstall_core.sh script. Be warned that it removes all installation of the sai2 core libraries, not only this one.



