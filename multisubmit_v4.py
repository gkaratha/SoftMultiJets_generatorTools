############### Code to simultaneously submit 
############### Original Author: George Karathanasis, CERN
#### usage: configure necessairy options  & run with "python multisubmit_v4.py" 


import os, subprocess
import datetime
import random

######################### configuration ###############################
Debug=False

Production="RunProduction.sh"
units_for_gen={"njobs":1,"nevts_per_job":100}
lfn_path = '/eos/cms/store/cmst3/group/softJets/gkaratha/'
flavor="workday"
year="2018"
Conditions="Run2" #Run2 Run3
cfg_regexp={"Run2":"Run2","Run3":"Run3"}


lhe_files={\
  "chain_m70_dm20":"/store/group/phys_smp/ZLFV/MC_generation/LHE_files/chain_m70_dm20.lhe",\
#  "chain_m70_dm8":"/store/group/phys_smp/ZLFV/MC_generation/LHE_files/chain_m70_dm8.lhe",\
#  "cascade_m100_31":"/store/group/phys_smp/ZLFV/MC_generation/LHE_files/cascade_m100_31.lhe",\
  "cascade_m220_67_20":"/store/group/phys_smp/ZLFV/MC_generation/LHE_files/cascade_m220_67_20.lhe"\
}

date=datetime.date.today().strftime('%m%d%Y')



###############################################################################
###############################################################################


Run2_CMSSWrel={'gen':'CMSSW_10_6_17_patch1','digi':'CMSSW_10_6_17_patch1','hlt':'CMSSW_10_2_16_UL','reco':'CMSSW_10_6_17_patch1','mini':'CMSSW_10_6_17_patch1','nano':'CMSSW_10_6_19_patch2'}

Run3_CMSSWrel={'gen':'CMSSW_13_0_14','digi':'CMSSW_13_0_14','hlt':'CMSSW_13_0_14','reco':'CMSSW_13_0_14','mini':'CMSSW_13_0_14','nano':'CMSSW_13_0_14'}

CMSSWrel={"Run2":Run2_CMSSWrel,"Run3":Run3_CMSSWrel}

if Conditions not in cfg_regexp.keys():
   print("conditions not found")
   exit()
if Conditions not in CMSSWrel.keys():
   print("conditions not found")
   exit()

def check_for_folder(path):
  if os.path.isdir(path):
    print path+" exists"
    os.system('rm -cdI -r '+path)



def load_grid():
   os.system("rm grid_val.txt")
   txt='#!/usr/bin/env bash\n'
   txt='PWD=`pwd`\n'
   txt+="export X509_USER_PROXY=${PWD}/proxy\n"
   txt+="voms-proxy-init --voms cms\n"
   txt+="grid-proxy-info >> grid_val.txt\n"
   with open('act_proxy.sh','w') as fl:
      fl.write(txt)
   os.system('. ./act_proxy.sh')
   kill = False
   with open('grid_val.txt','r') as fl2:
     lines = fl2.readlines()
     for line in lines:
       if "ERROR" in line.split(): 
           kill = True
   if kill:
      print ("wrong grid authentication")
      exit()


if __name__ == '__main__':
   if not Debug:
      load_grid()
   num = int(random.random()*10000)
   cmssw = CMSSWrel[Conditions]['gen']+"/"+CMSSWrel[Conditions]['digi']+"/"+CMSSWrel[Conditions]['hlt']+"/"+CMSSWrel[Conditions]['reco']+"/"+CMSSWrel[Conditions]['mini']+"/"+CMSSWrel[Conditions]['nano']
   for lhe in lhe_files.keys():
     name = lhe+"_cfg"+Conditions+"_Run"+year+"_"+date
     if os.path.isdir("eos/cms/"+lhe):
        print(lhe,"not found")
        exit()
     if os.path.isdir("output_condor/"+name):
        os.system("rm -I -r *_condor/"+name)
     if os.path.isdir(lfn_path+"/"+name):
        os.system("rm -I -r "+lfn_path+"/"+name)
     check_for_folder("output_condor/"+name)
     check_for_folder("error_condor/"+name)
     check_for_folder("log_condor/"+name)
     for ijob in range(units_for_gen["njobs"]):  
       skip = ijob*units_for_gen["nevts_per_job"]
       if skip==0: skip=1
       line="universe = vanilla\n"
       line+="executable = "+Production+"\n"
       line+="arguments = {lhe} {path} {cmssw} {nevts} {skip} {lumi} {cfg} {ijob} {outdir} \n".format(
            lhe=lhe_files[lhe], path=os.getcwd(), cmssw=cmssw, nevts=units_for_gen["nevts_per_job"], skip=skip, lumi=num+ijob, cfg=cfg_regexp[Conditions], ijob=lhe+"_"+str(ijob), outdir=lfn_path+"/"+name   )
       line+="request_memory = 2500\n"
       line+='output = output_condor/{name}/job_{job}.out\n'.format(name=name,job=str(ijob))
       line+='error = error_condor/{name}/job_{job}.err\n'.format(name=name,job=str(ijob))
       line+='log = log_condor/{name}/job_{job}.log\n'.format(name=name,job=str(ijob))
       line+='transfer_output_files   = ""\n'
       line+='+JobFlavour = \"{flavor}\" \n'.format(flavor=flavor)
       line+="queue\n"
       with open("condor_temp.sub",'w') as out:
         out.write(line);
         out.close()
         print "submitting "+str(ijob)
         if not Debug:
           os.system('condor_submit condor_temp.sub')
           subprocess.check_output(['rm',"condor_temp.sub"])
         print "done"
      

   
