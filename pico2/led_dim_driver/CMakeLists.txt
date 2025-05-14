# Generated Cmake Pico project file

cmake_minimum_required(VERSION 3.13)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Initialise pico_sdk from installed location
# (note this can come from environment, CMake cache etc)

# == DO NOT EDIT THE FOLLOWING LINES for the Raspberry Pi Pico VS Code Extension to work ==
if(WIN32)
    set(USERHOME $ENV{USERPROFILE})
else()
    set(USERHOME $ENV{HOME})
endif()
set(sdkVersion 2.1.0)
set(toolchainVersion RISCV_RPI_2_0_0_5)
set(picotoolVersion 2.1.0)
set(picoVscode ${USERHOME}/.pico-sdk/cmake/pico-vscode.cmake)
if (EXISTS ${picoVscode})
    include(${picoVscode})
endif()
# ====================================================================================
set(PICO_BOARD pico2 CACHE STRING "Board type")

# Pull in Raspberry Pi Pico SDK (must be before project)
include(pico_sdk_import.cmake)

project(led_dim_driver C CXX ASM)

# Initialise the Raspberry Pi Pico SDK
pico_sdk_init()

# Add executable. Default name is the project name, version 0.1

add_executable(led_dim_driver
        appbuild.h
        main.c
        )

# pull in common dependencies and additional uart hardware support
target_link_libraries(led_dim_driver pico_stdlib hardware_uart hardware_adc hardware_pwm)

# pre-build for the application.
add_custom_target(
 run ALL
 COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/prebuild.py ${CMAKE_CURRENT_SOURCE_DIR}
 BYPRODUCTS appbuild.h
 COMMENT "Generating enums"
)

add_dependencies(led_dim_driver run)
# end of pre-build

# create map/bin/hex file etc.
pico_add_extra_outputs(led_dim_driver)

# add url via pico_set_program_url
