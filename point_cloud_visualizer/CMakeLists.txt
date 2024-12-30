cmake_minimum_required(VERSION 3.20)

set(CMAKE_CXX_STANDARD 20)

project(point-cloud-viz LANGUAGES CXX)

# Specify output paths for all configurations.
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_DEBUG ${CMAKE_BINARY_DIR}/bin/debug)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_DEBUG ${CMAKE_BINARY_DIR}/bin/debug)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG ${CMAKE_BINARY_DIR}/bin/debug)

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_RELEASE ${CMAKE_BINARY_DIR}/bin/release)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE ${CMAKE_BINARY_DIR}/bin/release)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_BINARY_DIR}/bin/release)

include(FetchContent)

# imgui for the editor ui.
FetchContent_Declare(
    imgui
    GIT_REPOSITORY https://github.com/ocornut/imgui
    GIT_TAG 475453668d7da1662bf90266c5f0df0259705987
    GIT_PROGRESS TRUE
)

# SDL3 for input / window creation and handling.
FetchContent_Declare(
    SDL3
	GIT_REPOSITORY https://github.com/libsdl-org/SDL
	GIT_TAG ac13ca9ab691e13e8eebe9684740ddcb0d716203
	GIT_PROGRESS TRUE
)

FetchContent_Declare(
   dxtex 
   GIT_TAG main
	GIT_REPOSITORY https://github.com/microsoft/DirectXTex
	GIT_PROGRESS TRUE
)


FetchContent_MakeAvailable(imgui dxtex)


FetchContent_MakeAvailable(SDL3)

add_library(libimgui
    ${imgui_SOURCE_DIR}/imgui.cpp
    ${imgui_SOURCE_DIR}/imgui_demo.cpp
    ${imgui_SOURCE_DIR}/imgui_draw.cpp
    ${imgui_SOURCE_DIR}/imgui_widgets.cpp
    ${imgui_SOURCE_DIR}/imgui_tables.cpp
    ${imgui_SOURCE_DIR}/backends/imgui_impl_sdl2.cpp
    ${imgui_SOURCE_DIR}/backends/imgui_impl_dx11.cpp
)

target_include_directories(libimgui PUBLIC 
    ${imgui_SOURCE_DIR} 
    ${imgui_SOURCE_DIR}/backends
    ${sdl3_SOURCE_DIR}/include
)

target_link_libraries(libimgui PUBLIC SDL2::SDL2)
# stb for image loading.

FetchContent_Declare(
    stb
    GIT_REPOSITORY https://github.com/nothings/stb
    GIT_TAG 8b5f1f37b5b75829fc72d38e7b5d4bcbf8a26d55
    GIT_PROGRESS TRUE
)

FetchContent_MakeAvailable(stb)

add_executable(point-cloud-viz src/Application.cpp src/Camera.cpp src/Engine.cpp src/Main.cpp)

target_link_libraries(point-cloud-viz PRIVATE SDL2::SDL2 libimgui DirectXTex) 
target_include_directories(point-cloud-viz PRIVATE ${sdl3_SOURCE_DIR}/include ${dxtex_SOURCE_DIR} ${stb_SOURCE_DIR})
target_include_directories(point-cloud-viz PRIVATE include)

target_link_libraries(point-cloud-viz PRIVATE d3d11.lib dxgi.lib d3dcompiler.lib winmm.lib dxguid.lib)
