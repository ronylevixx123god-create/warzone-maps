#!/bin/sh
# send console command(s) to the WarzoneTest server and print the new log lines.  usage: wzc.sh [-w secs] "cmd1" ["cmd2" ...]
WAIT=4; if [ "$1" = "-w" ]; then WAIT=$2; shift 2; fi
LOG=/c/Users/levir/AstroPvP-WarzoneTest/logs/latest.log
CMD=/c/Users/levir/AstroPvP-Scripts/run-tests/warzonetest.cmd
N=$(wc -l < "$LOG")
for c in "$@"; do printf '%s\n' "$c" >> "$CMD"; done
sleep "$WAIT"
tail -n +$((N + 1)) "$LOG" | sed 's/^\[[0-9:]*\] \[Server thread\/INFO\]: //'
