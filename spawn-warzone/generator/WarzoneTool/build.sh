#!/bin/sh
# builds WarzoneTool.jar against the live server's jars (read only; nothing is written there)
set -e
cd "$(dirname "$0")"
S="C:/Users/levir/AstroPvP-Windows-Test"
J="/c/Program Files/Eclipse Adoptium/jdk-8.0.504.1-hotspot/bin"
rm -rf out && mkdir -p out
"$J/javac" -source 8 -target 8 -encoding UTF-8 -nowarn -d out -cp "$S/server.jar;$S/plugins/FastAsyncWorldEdit.jar;$S/plugins/worldedit-bukkit-6.1.7.3.jar" $(find src -name '*.java')
cp plugin.yml out/
(cd out && "$J/jar" cf ../WarzoneTool.jar .)
echo built WarzoneTool.jar
