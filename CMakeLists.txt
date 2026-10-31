cmake_minimum_required(VERSION 3.8)
project(navigation)

find_package(ament_cmake REQUIRED)

install(DIRECTORY worlds models launch config maps rviz
  DESTINATION share/${PROJECT_NAME})

install(PROGRAMS scripts/patrol.py scripts/cmd_vel_relay.py
  DESTINATION lib/${PROJECT_NAME})

ament_package()
