#include <filesystem>

#include "MainRedisInterface.h"
#include "controller/RobotControllerConfigParser.h"

int main(int argc, char** argv) {
	std::string config_file = "single_panda.xml";
	if (argc > 1) {
		config_file = argv[1];
	}

	std::string config_folder = std::string(CONFIG_FOLDER_PATH);

	// add world file folder to search path for parser
	Sai2Model::URDF_FOLDERS["WORLD_FILES_FOLDER"] =
		config_folder + "/world_files";
	Sai2Model::URDF_FOLDERS["ROBOT_FILES_FOLDER"] =
		config_folder + "/robot_files";

	// define the xml files folder. Only config files in that folder can be used
	// by this application
	std::string xml_files_folder = config_folder + "/xml_config_files";

	// support providing the config file with a relative path for convenience
	size_t last_slash_position = config_file.find_last_of("/\\");

	if (last_slash_position != std::string::npos) {
		std::string provided_relative_folder =
			config_file.substr(0, last_slash_position);
		std::filesystem::path absolute_provided_config_folder =
			std::filesystem::current_path().append(provided_relative_folder);

		if (absolute_provided_config_folder.lexically_normal() !=
			xml_files_folder) {
			std::cout
				<< "Incorrect folder provided in the relative path of the "
				   "config file. The file should be located in the folder : "
				<< xml_files_folder << std::endl;
			return -1;
		}

		config_file = config_file.substr(last_slash_position + 1);
	}

	Sai2Interfaces::MainRedisInterface main_interface(xml_files_folder,
													  config_file);

	return 0;
}