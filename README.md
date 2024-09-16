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

You can start OpenSai main application with a given config file in 4 steps:
1. Start the redis server (if not already running). In a new terminal, type `redis-server`
2. Start the OpenSai main application and provide a config file as argument. The config files must be in the `config_folder/xml_config_files` folder. If no config file name is provided, it will use the `single_panda.xml` file by default

```
./bin/OpenSai_main <optional-config-file-name>
```

3. Start the webui server with the generated file from the main application

```
python3 bin/ui/server.py config_folder/xml_config_files/webui_generated_file/webui.html
```

4. Open a web browser and navigate to `localhost:8000`

Alternatively, we provide a script that performs the first 3 steps automatically and you can provide the config file name as argument

```
sh scripts/launch.sh <optional-config-file-name>
```

If using the script, you will still need to manually open a web browser and navigate to `localhost:8000` in order to use the webui.

From the UI, you can load any config file from the `config_folder/xml_config_files` folder and interact with the robot controllers. Files in other folders will not work.
You can make new applications by making new config files and placing them in the `config_folder/xml_config_files` folder.

## Documentation

OpenSai main application is an instance of the MainRedisInterface application from the [sai2-interfaces](https://github.com/manips-sai-org/sai2-interfaces) library. You can interact with the controller and simulation from the webui on the browser. For an overview of the ui and how to use it, see [this page](https://github.com/manips-sai-org/sai2-interfaces/blob/master/docs/ui_overview.md). For details on the config files, how to use them and how to make your own for your application, see [here](https://github.com/manips-sai-org/sai2-interfaces/blob/master/docs/config_files_details.md).

## Updating the core libraries

To pull the latest updates from the core libraries, you can use the provided script that will checkout the master branch of all core libraries and pull the latest changes.

```
sh scripts/update_core_libraries.sh
```

Don't forget to re install them afterwards, and to re build the main application.

## Uninstall instructions

The core libraries are installed for the current OS session user, and the main application is not installed globally. The uninstall script will remove the build and cmake output for all core libraries and the main application:

```
sh scripts/uninstall.sh
```
