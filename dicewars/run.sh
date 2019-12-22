#!/bin/bash

. path.sh

touch out.txt

echo "Bots: msv, ste, stei, wpm_c, wpm_d, wpm_s" >> out.txt

echo "### 3 PLAYERS ###" >> out.txt
./scripts/dicewars-ai-only.py --debug --logdir logs/ --ai msv dt.ste dt.stei --nb-games 100 >> out.txt
echo >> out.txt
./scripts/dicewars-ai-only.py --debug --logdir logs/ --ai msv dt.ste dt.wpm_c --nb-games 100 >> out.txt
echo >> out.txt
./scripts/dicewars-ai-only.py --debug --logdir logs/ --ai msv dt.ste dt.wpm_d --nb-games 100 >> out.txt
echo >> out.txt
./scripts/dicewars-ai-only.py --debug --logdir logs/ --ai msv dt.ste dt.wpm_s --nb-games 100 >> out.txt
echo >> out.txt
./scripts/dicewars-ai-only.py --debug --logdir logs/ --ai msv dt.stei dt.wpm_c --nb-games 100 >> out.txt
echo >> out.txt
./scripts/dicewars-ai-only.py --debug --logdir logs/ --ai msv dt.stei dt.wpm_d --nb-games 100 >> out.txt
echo >> out.txt
./scripts/dicewars-ai-only.py --debug --logdir logs/ --ai msv dt.stei dt.wpm_s --nb-games 100 >> out.txt
echo >> out.txt
./scripts/dicewars-ai-only.py --debug --logdir logs/ --ai msv dt.wpm_c dt.wpm_d --nb-games 100 >> out.txt
echo >> out.txt
./scripts/dicewars-ai-only.py --debug --logdir logs/ --ai msv dt.wpm_c dt.wpm_s --nb-games 100 >> out.txt
echo >> out.txt
./scripts/dicewars-ai-only.py --debug --logdir logs/ --ai msv dt.wpm_d dt.wpm_s --nb-games 100 >> out.txt
echo >> out.txt

echo "### 4 PLAYERS ###" >> out.txt
./scripts/dicewars-ai-only.py --debug --logdir logs/ --ai msv dt.ste dt.stei dt.wpm_c --nb-games 150 >> out.txt
echo >> out.txt
./scripts/dicewars-ai-only.py --debug --logdir logs/ --ai msv dt.ste dt.stei dt.wpm_d --nb-games 150 >> out.txt
echo >> out.txt
./scripts/dicewars-ai-only.py --debug --logdir logs/ --ai msv dt.ste dt.stei dt.wpm_s --nb-games 150 >> out.txt
echo >> out.txt
./scripts/dicewars-ai-only.py --debug --logdir logs/ --ai msv dt.stei dt.wpm_c dt.wpm_d --nb-games 150 >> out.txt
echo >> out.txt
./scripts/dicewars-ai-only.py --debug --logdir logs/ --ai msv dt.stei dt.wpm_c dt.wpm_s --nb-games 150 >> out.txt
echo >> out.txt
./scripts/dicewars-ai-only.py --debug --logdir logs/ --ai msv dt.stei dt.wpm_d dt.wpm_s --nb-games 150 >> out.txt
echo >> out.txt
./scripts/dicewars-ai-only.py --debug --logdir logs/ --ai msv dt.wpm_c dt.wpm_d dt.wpm_s --nb-games 150 >> out.txt
echo >> out.txt

echo "### 5 PLAYERS ###" >> out.txt
./scripts/dicewars-ai-only.py --debug --logdir logs/ --ai msv ste stei wpm_c wpm_d --nb-games 200 >> out.txt
echo >> out.txt
./scripts/dicewars-ai-only.py --debug --logdir logs/ --ai msv wpm_s stei wpm_c wpm_d --nb-games 200 >> out.txt
echo >> out.txt
./scripts/dicewars-ai-only.py --debug --logdir logs/ --ai msv ste wpm_s wpm_c wpm_d --nb-games 200 >> out.txt
echo >> out.txt
./scripts/dicewars-ai-only.py --debug --logdir logs/ --ai msv ste stei wpm_s wpm_d --nb-games 200 >> out.txt
echo >> out.txt
./scripts/dicewars-ai-only.py --debug --logdir logs/ --ai msv ste stei wpm_c wpm_s --nb-games 200 >> out.txt
echo >> out.txt
