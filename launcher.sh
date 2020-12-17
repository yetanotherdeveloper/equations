#!/bin/bash

xinput --disable 13  # Disable mouse
/home/jacek-home/projects/equations/equations.py
if [ $? -ne 111 ]
then
	sudo shutdown -h now
fi
xinput --enable 13   # Enable mouse
