############### Code to generate events in pythia given LHE file
############### Original Author: George Karathanasis, CERN
#### usage: ./CascadeProduction.sh <LHE> <LOCAL_PATH> <CMSSW_REL> <EVTS_PRODUCE> <SKIP_EVTS> <LUMI> <CFG.py> <JOB_NUMBER> <OUTPUT_PATH>

#!/bin/bash


LHE=$1
shift;
echo "LHE: ${LHE}"
PTH=$1
shift;
echo "PATH: ${PTH}"
CMSSW=$1
shift;
echo "CMSSW: ${CMSSW}"
EVTS=$1
shift;
echo "EVENTS: ${EVTS}"
SKIP=$1
shift;
echo "SKIP: ${SKIP}"
LUMI=$1
shift;
echo "LUMI: ${LUMI}"
CFG=$1
shift;
echo "CFG: ${CFG}_step*_cfg.py"
JOB=$1
shift;
echo "JOB: ${JOB}"
OUT=$1
shift;
echo "OUTPUT: ${OUT}"

cp $PTH/${CFG}_step*_cfg.py .

PWD=`pwd`

CMSSWS=($(echo $CMSSW | tr "/" "\n"))

echo "$PTH/${CMSSWS[0]}/src"

echo "Step1 gen sim"
cd $PTH/${CMSSWS[0]}/src
eval $(scramv1 runtime -sh)
pwd
cd -
cmsRun ${CFG}_stepGen_cfg.py lhe=${LHE} nEvts=${EVTS} skip=${SKIP} lumi=${LUMI} output=${JOB}_step1_gensim 

echo "Step2 digi"
cd $PTH/${CMSSWS[1]}/src
eval $(scramv1 runtime -sh)
#echo pwd
#pwd
#echo gh
cd -
cmsRun ${CFG}_stepDigi_cfg.py infile=${JOB}_step1_gensim.root output=${JOB}_step2_digi

echo "Step3 HLT"
cd $PTH/${CMSSWS[2]}/src
eval $(scramv1 runtime -sh)
#echo pwd
#pwd
#echo gh
cd -
cmsRun ${CFG}_stepHLT_cfg.py infile=${JOB}_step2_digi.root output=${JOB}_step3_hlt

echo "Step4 reco"
cd $PTH/${CMSSWS[3]}/src
eval $(scramv1 runtime -sh)
cd -
cmsRun ${CFG}_stepReco_cfg.py infile=${JOB}_step3_hlt.root output=${JOB}_step4_reco

echo "Step5 mini"
cd $PTH/${CMSSWS[4]}/src
eval $(scramv1 runtime -sh)
cd -
cmsRun ${CFG}_stepMini_cfg.py infile=${JOB}_step4_reco.root output=${JOB}_step5_mini

#cd $PTH/${CMSSWS[5]}/src
#eval $(scramv1 runtime -sh)
#cd -
#cmsRun ${CFG}_stepReco_cfg.py infile=${JOB}_step5_mini output=${JOB}_step6_nano


mkdir -p ${OUT}/Mini
#mkdir -p ${OUT}/Nano

cp ${JOB}_step5_mini.root ${OUT}/Mini
#cp ${JOB}_step6_nano.root ${OUT}/Nano

#echo "job ${JOB} done!"
#
