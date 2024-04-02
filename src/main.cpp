#include "MainRedisInterface.h"

int main(int argc, char** argv) {
	if (argc < 2) {
		std::cout
			<< "Provide the path to the config folder (and optionnally the "
			   "initial config file name). For example:\n\t./OpenSai_main "
			   "../config_folder single_panda.xml"
			<< std::endl;
		return -1;
	}

	const std::string config_folder = argv[1];

	std::string config_file = "";
	if(argc > 2) {
		config_file = argv[2];
	}

	// add world file folder to search path for parser
	Sai2Model::URDF_FOLDERS["WORLD_FILES_FOLDER"] =
		config_folder + "/world_files";
	Sai2Model::URDF_FOLDERS["ROBOT_FILES_FOLDER"] =
		config_folder + "/robot_files";

	// define the config folder. Only config files in that folder can be used by
	// this application
	std::string config_folder_path =
		config_folder + "/main_configs";

	// // initial config file (optionnal)
	// std::string config_file = "single_panda.xml";

	Sai2Interfaces::MainRedisInterface main_interface(config_folder_path,
													  config_file);

	return 0;
}