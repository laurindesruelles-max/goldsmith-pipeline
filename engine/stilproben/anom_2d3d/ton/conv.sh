#!/bin/sh
# usage: conv.sh <name> <speed_factor> <pad_seconds>
R=/home/claude/anom/r/$1; O=/home/claude/anom/remo/public/$1.mp4
ffmpeg -v error -y -framerate 12 -pattern_type glob -i "$R/f_*.png" \
  -vf "setpts=$2*PTS,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,scale=1920:1080:flags=lanczos,unsharp=5:5:0.6,eq=contrast=1.04:saturation=1.05,tpad=stop_mode=clone:stop_duration=$3" \
  -c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p $O
ffprobe -v error -show_entries format=duration -of csv=p=0 $O
