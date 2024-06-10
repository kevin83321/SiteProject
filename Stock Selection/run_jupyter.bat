@echo off
rem change drive to where this app located
%~d0 

rem change directory to app located
cd %~dp0

jupyter notebook