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

# SAI2-COMMON
find_package(SAI2-COMMON REQUIRED)
include_directories(${SAI2-COMMON_INCLUDE_DIRS})

# SAI2-URDF
find_package(SAI2-URDF REQUIRED)
include_directories(${SAI2-URDF_INCLUDE_DIRS})

# SAI2-MODEL
find_package(SAI2-MODEL REQUIRED)
include_directories(${SAI2-MODEL_INCLUDE_DIRS})

# SAI2-SIMULATION
find_package(SAI2-SIMULATION REQUIRED)
include_directories(${SAI2-SIMULATION_INCLUDE_DIRS})
add_definitions(${SAI2-SIMULATION_DEFINITIONS})

# SAI2-GRAPHICS
find_package(SAI2-GRAPHICS REQUIRED)
include_directories(${SAI2-GRAPHICS_INCLUDE_DIRS})
add_definitions(${SAI2-GRAPHICS_DEFINITIONS})

# SAI2-PRIMITIVES
find_package(SAI2-PRIMITIVES REQUIRED)
include_directories(${SAI2-PRIMITIVES_INCLUDE_DIRS})

# SAI2-INTERFACES
find_package(SAI2-INTERFACES REQUIRED)
include_directories(${SAI2-INTERFACES_INCLUDE_DIRS})

# application
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/bin)
file(MAKE_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})

set(OPENSAI_LIBRARIES
${SAI2-GRAPHICS_LIBRARIES}
${SAI2-URDF_LIBRARIES}
${CHAI3D_LIBRARIES}
${SAI2-INTERFACES_LIBRARIES}
${SAI2-PRIMITIVES_LIBRARIES}
${SAI2-MODEL_LIBRARIES}
${SAI2-SIMULATION_LIBRARIES}
${SAI2-COMMON_LIBRARIES}
)

add_executable(OpenSai_main src/main.cpp)
target_link_libraries(OpenSai_main ${OPENSAI_LIBRARIES})

file(CREATE_LINK ${SAI2-INTERFACES_UI_DIR}
     ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/ui SYMBOLIC)
