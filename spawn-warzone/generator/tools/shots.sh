#!/bin/sh
# real client screenshots: shots.sh <pid> <outdir> then lines "name x y z yaw pitch" on stdin
PID=$1; OUT=$2; W=$(dirname "$0")/wzc.sh; SP='C:\Users\levir\wt-warzone\camera'
while read n x y z yaw pitch; do
  [ -z "$n" ] && continue
  sh "$W" -w 5 "tp WarzoneCam $x $y $z $yaw $pitch" > /dev/null
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$SP\restore.ps1" -ProcId $PID > /dev/null
  sleep 2
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$SP\shot.ps1" -ProcId $PID -Out "$OUT/$n.png"
done
