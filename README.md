# Comparator

GTK4 application to display Minecraft server status.

![comparator-screenshot1](https://user-images.githubusercontent.com/98206524/153707887-e08c240d-76da-42b7-83c8-64818aeb3948.png)


## Features
* display servers icon, description, version and online players
* detect server on localhost
* show LAN worlds
* formatted descriptions (including obfuscated text)

## Used technologies
* GTK, libadwaita - user interface
* [mcstatus](https://github.com/Dinnerbone/mcstatus)
* `ss` for detecting open ports to display localhost servers
* Python

## Why it is written in Python
* There is Python module [mcstatus](https://github.com/Dinnerbone/mcstatus)
* This was **very** small project at the beggining.
