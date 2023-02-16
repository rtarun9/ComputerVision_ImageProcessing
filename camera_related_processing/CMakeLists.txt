include(FetchContent)

project (camera-processing CXX)

FetchContent_Declare(
    opencv
    GIT_REPOSITORY https://github.com/opencv/opencv
    GIT_TAG 4.7.0
    GIT_PROGRESS TRUE
)

FetchContent_MakeAvailable(opencv)

add_executable(focal_radius_approximation)