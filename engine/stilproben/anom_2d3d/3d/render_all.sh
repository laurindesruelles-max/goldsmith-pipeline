#!/bin/sh
cd /home/claude/anom/3d
R=/home/claude/anom/r
SHOT=hook SAMPLES=8 python3 phone_scene.py $R/hook > $R/hook.log 2>&1
python3 server_scene.py $R/server > $R/server.log 2>&1
python3 evidence_scene.py $R/evidence > $R/evidence.log 2>&1
SHOT=end SAMPLES=8 python3 phone_scene.py $R/end > $R/end.log 2>&1
echo ALLDONE > $R/done.txt
