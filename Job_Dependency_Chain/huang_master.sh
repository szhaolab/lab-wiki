#!/bin/bash

cd /dartfs/rc/lab/S/Szhao/perturbation_prediction/SeqExpDesign/vcc/data/

split_script=/dartfs/rc/lab/S/Szhao/perturbation_prediction/SeqExpDesign/vcc/data/huang_split_qiruiz_auto.sh
wilcoxon_script=/dartfs/rc/lab/S/Szhao/perturbation_prediction/SeqExpDesign/vcc/data/huang_wilcoxon_qiruiz.sh

prev_dep=""

for x in {1..2}; do
  if [[ -n "$prev_dep" ]]; then
      dep_opt="--dependency=afterok:${prev_dep}"
  else
      dep_opt=""
  fi

  jid_split=$(sbatch --parsable $dep_opt \
                     --export=IDX=$x "$split_script")
  echo "[+] Split $x  →  JobID $jid_split"

  beg=$((200*(x-1)+1))
  end=$((200*x))

  jid_wil=$(sbatch --parsable --array=${beg}-${end} \
                   --dependency=afterok:${jid_split} \
                   "$wilcoxon_script")
  echo "    ↳ Wilcoxon ${beg}-${end}  →  JobID $jid_wil"

  prev_dep=$jid_wil
done
