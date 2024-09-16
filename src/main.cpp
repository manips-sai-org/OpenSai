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

	Sai2Interfaces::MainRedisInterface main_interface(xml_files_folder,
													  config_file);

	return 0;
}