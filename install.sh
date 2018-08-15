#!/bin/bash
##########################################################################
# Script for installing todo program.
##########################################################################

#Check that the user is root
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi

# Copy the file
cp ./todo.py /usr/local/bin/todo

# Make the file executable
chmod +x /usr/local/bin/todo

echo "Finished.."

exit
