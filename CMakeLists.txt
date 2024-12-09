cmake_minimum_required(VERSION 3.10)

project(OPENSAI)
set(PROJECT_VERSION 0.1.0)

set(CMAKE_CXX_FLAGS "-std=c++17 -I/usr/include -I/usr/local/include -fPIC")
if(${CMAKE_SYSTEM_NAME} MATCHES Darwin)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -I/opt/homebrew/include")
endif()

# set default build to release
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  message(STATUS "Setting build type to 'Release' as none was specified.")
  set(CMAKE_BUILD_TYPE Release)
endif()

# include Eigen
find_package(Eigen3 REQUIRED)
include_directories(${EIGEN3_INCLUDE_DIR})

# include Chai3d
find_package(CHAI3D REQUIRED)
include_directories(${CHAI3D_INCLUDE_DIRS})
add_definitions(${CHAI3D_DEFINITIONS})
link_directories(${CHAI3D_LIBRARY_DIRS})

# SAI-COMMON
find_package(SAI-COMMON REQUIRED)
include_directories(${SAI-COMMON_INCLUDE_DIRS})

# SAI-URDF
find_package(SAI-URDF REQUIRED)
include_directories(${SAI-URDF_INCLUDE_DIRS})

# SAI-MODEL
find_package(SAI-MODEL REQUIRED)
include_directories(${SAI-MODEL_INCLUDE_DIRS})

# SAI-SIMULATION
find_package(SAI-SIMULATION REQUIRED)
include_directories(${SAI-SIMULATION_INCLUDE_DIRS})
add_definitions(${SAI-SIMULATION_DEFINITIONS})

# SAI-GRAPHICS
find_package(SAI-GRAPHICS REQUIRED)
include_directories(${SAI-GRAPHICS_INCLUDE_DIRS})
add_definitions(${SAI-GRAPHICS_DEFINITIONS})

# SAI-PRIMITIVES
find_package(SAI-PRIMITIVES REQUIRED)
include_directories(${SAI-PRIMITIVES_INCLUDE_DIRS})

# SAI-INTERFACES
find_package(SAI-INTERFACES REQUIRED)
include_directories(${SAI-INTERFACES_INCLUDE_DIRS})

# application
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/bin)
file(MAKE_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})

set(OPENSAI_LIBRARIES
${SAI-GRAPHICS_LIBRARIES}
${SAI-URDF_LIBRARIES}
${CHAI3D_LIBRARIES}
${SAI-INTERFACES_LIBRARIES}
${SAI-PRIMITIVES_LIBRARIES}
${SAI-MODEL_LIBRARIES}
${SAI-SIMULATION_LIBRARIES}
${SAI-COMMON_LIBRARIES}
)

add_executable(OpenSai_main src/main.cpp)
target_link_libraries(OpenSai_main ${OPENSAI_LIBRARIES})

set( CONFIG_FOLDER_PATH ${PROJECT_SOURCE_DIR}/config_folder )
add_definitions(-DCONFIG_FOLDER_PATH="${CONFIG_FOLDER_PATH}")

file(CREATE_LINK ${SAI-INTERFACES_UI_DIR}
     ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/ui SYMBOLIC)
