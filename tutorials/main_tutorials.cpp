#include <filesystem>

#include "MainRedisInterface.h"

int main(int argc, char** argv) {
	std::string config_file;
	if (argc > 1) {
		config_file = argv[1];
	} else {
		std::cout << "Please provide the config file as an argument" << std::endl;
		return -1;
	}

	std::string config_folder = std::string(TUTORIALS_CONFIG_FOLDER_PATH);

	// add world file folder to search path for parser
	SaiModel::URDF_FOLDERS["TUTORIALS_WORLD_FILES_FOLDER"] =
		config_folder + "/world_files";
	SaiModel::URDF_FOLDERS["TUTORIALS_ROBOT_FILES_FOLDER"] =
		config_folder + "/robot_files";

	// define the xml files folder. Only config files in that folder can be used
	// by this application
	std::string xml_files_folder = config_folder + "/xml_files";
	SaiInterfaces::MainRedisInterface main_interface(xml_files_folder,
													  config_file);

	return 0;
}