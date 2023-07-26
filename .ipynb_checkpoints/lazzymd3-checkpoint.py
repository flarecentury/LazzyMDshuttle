import matplotlib.pyplot as plt
import numpy as np
import MDAnalysis as mda
from MDAnalysis.coordinates.memory import MemoryReader
from MDAnalysis.analysis.base import AnalysisFromFunction
import nglview as nv
import time
import os
import paramiko
import shutil
from ipylab import JupyterFrontEnd
import ipynbname
import subprocess
import tempfile
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from ipywidgets import interact
import math
from functools import partial
from concurrent import futures 
import multiprocess as mp
from multiprocess import Pool,cpu_count
import time
from functools import partial
from itertools import repeat

########
class niceday():
    ## lammps log
    def __init__(self, node, PJname,PJdir):
        self.PJdir=PJdir
        self.node = node
        self.PJname = PJname
        self.inputfile = 'in.' + PJname
        self.trajs = 'dcd.' + PJname + '.dcd'
        self.lammpstrj = 'lammpstrj.' + PJname + '.lammpstrj'
        self.lammpslog = 'log.' + PJname
        self.slurmlog = 'Output.' + self.inputfile
        self.slurmerrorlog = 'Error.' + self.inputfile
        self.L_workdir = PJdir + PJname + '/'
        self.L_input = self.L_workdir + '#input/'
        self.L_tmp = self.L_workdir + 'tmp/'
        self.L_traj = self.L_workdir + 'tmp/'
        self.L_log = self.L_workdir + 'tmp/'
        self.L_reax = self.L_workdir + 'tmp/'
        self.L_analysis = self.L_workdir + '#analysis/'
        Origin_L_folders = [self.L_input, self.L_tmp, self.L_traj, self.L_log, self.L_reax,self.L_analysis]
        self.L_folders = list(set(Origin_L_folders))
        self.L_foldernames = [i.rsplit('/', 2)[-2] for i in self.L_folders]
        
        if node != 'jupyter':
            self.R_workdir = PJdir.replace('MD_domain','MD-analysis') + PJname + '/'
            self.channel, self.ftp = self.select_channel(self.node)
            self.job = 'source /home/flare/.bashrc && cd ' + self.R_workdir + ' && ulimit -c unlimited && sbatch -J ' + self.inputfile + ' '
        if node == 'jupyter': 
            self.R_workdir = PJdir.replace('MD_domain','MD-analysis').replace('flare','lym') + PJname + '/'
            self.job = 'cd ' + self.R_workdir + ' && ulimit -c unlimited && sbatch -J ' + self.inputfile + ' '
            try:
                print('Approaching the previous landing site')
                self.previous_working_node,self.previous_working_dir=self.previous_working_info()
                print('Tring to land on site:',self.previous_working_node)
                self.channel, self.ftp = self.select_channel(self.previous_working_node)

                if self.previous_working_node == 'node1':
                    partition = 'xeon72_broadwell'
                elif self.previous_working_node == 'node2':
                    partition = 'epyc128_zen'
                elif self.previous_working_node == 'node3':
                    partition = 'epyc128_zen2'
                elif self.previous_working_node == 'node20':
                    partition = 'flare_private'
                elif self.previous_working_node == 'node21':
                    partition = 'flare_private'
                else:
                    if 'node' in self.previous_working_node:
                        partition = 'Nebula32_zen3'
                    else:
                        partition = 'UNKNOW'
                print('Successfully landed on planet',partition)
                print('==============================================')
                pic().jupyter()
                print('==========================================================================')
            except:
                try:
                    print('Previous landing site is not avaliable, decting..')
                    current_working_node = self.current_working_node()
                    self.channel, self.ftp = self.select_channel(current_working_node)
                    print('Landing on',current_working_node)
                except:
                    print('The terrain of the landing site is arduous, landing on jupyter temporarily')
                    self.channel, self.ftp = self.select_channel('jupyter')
                    print('==========================================================================')
                    pic().sun()
                    print('==========================================================================')
        
        self.R_foldername = self.R_workdir.rsplit('/', 2)[-2]
        self.mkdir()
        self.mkipynb0()

    ##### prepare #####
    def mkdir(self): # 20220608
        L_workdir = self.L_workdir
        R_workdir = self.R_workdir
        L_folders = self.L_folders
        PJname = self.PJname
        L_foldernames = self.L_foldernames
        channel = self.channel
        try:
            command = 'mkdir -p ' + R_workdir
            self.sendcommand(channel, 0, command=command )
            self.ftp.mkdir(R_workdir)
            print('Done making R_workdir')
        except IOError:
            print("Remote folder exists: ", R_workdir)
        try:
            os.makedirs(L_workdir)
            print('Done making L_workdir')
        except IOError:
            print("Main local folder exists: ", L_workdir)
        for folder in L_folders:
            try:
                os.makedirs(folder)
                done = 0
            except IOError:
                done = 1
        if done == 1:
            print("Local folders exist: " + ','.join(L_foldernames))
        if done == 0:
            print('Done making L_folders')
        ### create input file
        try:
            with open(self.L_input + self.inputfile, 'r') as r:
                ggg = r
        except:
            print('# Create a new input file! Happy MD simulation')
            with open(self.L_input + self.inputfile, 'w') as f:
                f.write(
                    '# '+L_workdir+'\n# Create a new input file! Happy MD simulation\n# Initialization\nvariable name index ' + PJname + '\n')

    def savenotebook(self):
        # method 1
        app = JupyterFrontEnd()

        # app.commands.list_commands()  必须在下方不同cell里运行！！！

        # method 2
        # from IPython.display import display, HTML
        # script = """
        # this.nextElementSibling.focus();
        # this.dispatchEvent(new KeyboardEvent('keydown', {key:'s', keyCode: 83, ctrlKey: true}));
        # """
        # display(HTML((
        #     '<img src onerror="{}" style="display:none">'
        #     '<input style="width:0;height:0;border:0">'
        # ).format(script)))
        app.commands.execute('docmanager:save')

    def mkipynb0(self):
        # self.savenotebook()
        PJname = self.PJname
        L_workdir = self.L_workdir
        nb_fname = ipynbname.name()
        nb_path = ipynbname.path()
        node = self.node
        target = L_workdir + PJname + '_'+node
        print('Detecting notebook: ',target+'.ipynb')
        if str(nb_path) != str(target+'.ipynb'):
            if not os.path.isfile(target +'.ipynb'):
                with open(target+'.txt', 'w') as handle:
                    handle.write(str(self.current_login_Node(out=0)[0])+'\t'+str(self.current_login_Node(out=0)[1])+'\n')
                    
                print('----------------------------------------------------------------------------------')
                print("Project dones't exist, refuse to mk working dir")
                print('1. Creating new control file for the project')
                print('2. Backup the current notebook')
                shutil.copyfile(nb_path, str(nb_path) + '1')
                self.savenotebook()
                time.sleep(10)
                print('3. Copying: ', nb_path, ' to ', L_workdir + PJname + '.ipynb')
                shutil.copyfile(nb_path, target +'.ipynb')
                #     print('yes')
                # if str(nb_fname) != self.PJname:
                # app = JupyterFrontEnd()
                # app.commands.execute('docmanager:close')
                print('4. Restore the current notebook')
                shutil.copyfile(str(nb_path) + '1', nb_path)
                print('5. Removing backup')
                os.remove(str(nb_path) + '1')
                print('PLZ close this note book!!')
            else:
                print('Project alread exits')
       
        else:
            # self.mkdir()
            print('Env prepared!')

    ##### process #####
    def checkinput(self, out=1 ,filter='all'):
        ftp = self.ftp
        inputfile = self.inputfile
        R_workdir = self.R_workdir
        print('looking in ',R_workdir + inputfile)
        F = ftp.open(R_workdir + inputfile)
        f = F.readlines()
        com = []
        linenumbers = len(f)
        # print(linenumbers)
        if filter == 'all':
            for index, i in enumerate(f):
                line = i.split()
                line.insert(0, str(index))
                com.append(line)
            for k in com:
                # print(k[0],k[1],' '.join(k[2:]))
                if out == 1:
                    print(' '.join(k[0:]))
        else:
            for index, i in enumerate(f):
                if i.startswith(filter):
                    line = i.split()
                    line.insert(0, str(index))
                    com.append(line)
            for k in com:
                # print(k[0],k[1],' '.join(k[2:]))
                if out == 1:
                    print('\t'.join(k[0:]))
        if out == 1:
            print('-------------------------------')
        return com

    def totalsteps(self):
        totalsteps = 0
        for i in self.checkinput(out=0,filter='run'):
            totalsteps += int(i[-1])
        return totalsteps
    
    def checklog(self, refresh=1, Lastlog=0, Check_lammpslog=1, Check_slurmlog=1, Download_log=1, checklog_local=1):
        channel = self.channel
        R_workdir = self.R_workdir
        slurmerrorlog = self.slurmerrorlog
        L_log = self.L_log
        inputfile = self.inputfile
        lammpslog = self.lammpslog
        slurmlog = self.slurmlog
        ftp = self.ftp
 
        if refresh != 1:
            print('---------------------------------------------------------------------------------')
            print('Plotting local file! PLZ ensure that the data you are using is the latest version')
            print('--------------------------  version of local files--------------------------------')
            print(self.listlocallogfile(L_log + lammpslog))
            print(self.listlocallogfile(L_log + slurmlog))

        if refresh == 1:
            if checklog_local == 1 or Download_log == 1:
                if self.node=='jupyter':
                    
                    self.download(channel, R_workdir + slurmerrorlog, L_log + slurmerrorlog)
                    self.download(channel, R_workdir + slurmlog, L_log + slurmlog)
                    # try:
                    tmp_workdir='/tmp/'+'lym@'+self.current_job_id()+'/'
                    
                    if 'null' not in tmp_workdir:
                        self.download(channel, tmp_workdir + inputfile, L_log + inputfile + '_remote')
                        self.download(channel, tmp_workdir + lammpslog, L_log + lammpslog)
                        self.download(channel, tmp_workdir + inputfile+ '.out', L_log + inputfile+ '.out')
                        
                    else:
                        try:
                            tmp_workdir = self.previous_working_dir
                            print('downloading from previous_working_dir')
                            output=self.download(channel, tmp_workdir + inputfile, L_log + inputfile + '_remote')
                        except:
                            print('no info about previous_working_dir, using R_workdir')
                            tmp_workdir = R_workdir
                            output=self.download(channel, tmp_workdir + inputfile, L_log + inputfile + '_remote')
                            
                        if 'failed' in output:
                            print('previous_working_dir doesnt exist, downloading from R_workdir')
                            self.download(channel, R_workdir + inputfile, L_log + inputfile + '_remote')
                            self.download(channel, R_workdir + lammpslog, L_log + lammpslog)
                            self.download(channel, R_workdir + inputfile+ '.out', L_log + inputfile+ '.out')
                        else:
                            self.download(channel, tmp_workdir + lammpslog, L_log + lammpslog)
                            self.download(channel, tmp_workdir + inputfile+ '.out', L_log + inputfile+ '.out')
                else:
                    self.download(channel, R_workdir + slurmerrorlog, L_log + slurmerrorlog)
                    self.download(channel, R_workdir + slurmlog, L_log + slurmlog)
                    self.download(channel, R_workdir + inputfile, L_log + inputfile + '_remote')
                    self.download(channel, R_workdir + lammpslog, L_log + lammpslog)
                    self.download(channel, R_workdir + inputfile+ '.out', L_log + inputfile+ '.out')

        if Check_lammpslog == 1:
            logfile = lammpslog
            if checklog_local == 1:
                with open(L_log + logfile, encoding="utf8", errors='ignore') as log:
                    f = log.readlines()
                    print(L_log + logfile)
            else:
                log = ftp.open(R_workdir + logfile)
                f = log.readlines()
                print(R_workdir + logfile)
            print('lmplog 行数: ', len(f))
            print('================  WARNINGs ================')
            for i in f:
                if 'ERROR' in i:
                    print(i)
                if 'Last c' in i:
                    print(i)
                if 'WARNING:' in i:
                    print(i)
                if '@@@@@@@' in i:
                    print(i)
            print('================  Last logs ================')
            try:
                for i in range(len(f) - Lastlog, len(f)):
                    print(f[i])
                print('===' * 25)
            except:
                for i in range(len(f)):
                    print(f[i])
                print('===' * 25)

        if Check_lammpslog == 1 and Check_slurmlog == 1:
            # print('===='*20)
            print(('\n' + '\n') * 4)

        if Check_slurmlog == 1:
            logfile = slurmlog
            if checklog_local == 1:
                with open(L_log + logfile, encoding="utf8", errors='ignore') as log:
                    f = log.readlines()
                    print(L_log + logfile)
            else:
                log = ftp.open(R_workdir + logfile)
                f = log.readlines()
                print(R_workdir + logfile)
            print('slurmlog 行数: ', len(f))
            print('================  WARNINGs ================')
            for i in f:
                if 'ERROR' in i:
                    print(i)
                if 'Last c' in i:
                    print(i)
                if 'WARNING:' in i:
                    if 'Kokkos' not in i:
                        print(i)
                if '@@@@@@@' in i:
                    print(i)
            print('================  Last logs ================')
            print(len(f))
            for i in range(len(f) - Lastlog, len(f)):
                if 'Kokkos::' not in f[i]:
                    print(f[i])
            print('===' * 20)

    def plotlog(self, logfile, refresh=1, plot=True, a=0, b=-1, skip=1, plotlog_local=1):
        # use local file
        timestep = self.gettimestep() ## fs
        channel = self.channel
        R_workdir = self.R_workdir
        L_log = self.L_log
        ftp = self.ftp
        lammpslog = self.lammpslog
        slurmlog = self.slurmlog
        slurmerrorlog = self.slurmerrorlog
        inputfile = self.inputfile

        
        if refresh != 1:
            R_workdir = self.R_workdir
            print('---------------------------------------------------------------------------------')
            print('Plotting local file! PLZ ensure that the data you are using is the latest version')
            print('--------------------------  version of local files--------------------------------')
            print(self.listlocallogfile(L_log + lammpslog))
            print(self.listlocallogfile(L_log + slurmlog))
            
        if refresh == 1 and plotlog_local == 1:
            
            if self.node=='jupyter':
                self.download(channel, R_workdir + slurmerrorlog, L_log + slurmerrorlog)
                self.download(channel, R_workdir + slurmlog, L_log + slurmlog)
                # try:
                tmp_workdir='/tmp/'+'lym@'+self.current_job_id()+'/'

                if 'null' not in tmp_workdir:
                    self.download(channel, tmp_workdir + inputfile, L_log + inputfile + '_remote')
                    self.download(channel, tmp_workdir + lammpslog, L_log + lammpslog)
                    self.download(channel, tmp_workdir + inputfile+ '.out', L_log + inputfile+ '.out')

                else:
                    tmp_workdir = self.previous_working_dir
                    print('downloading from previous_working_dir')
                    output=self.download(channel, tmp_workdir + inputfile, L_log + inputfile + '_remote')
                    if 'failed' in output:
                        print('previous_working_dir doesnt exist, downloading from R_workdir')
                        self.download(channel, R_workdir + inputfile, L_log + inputfile + '_remote')
                        self.download(channel, R_workdir + lammpslog, L_log + lammpslog)
                        self.download(channel, R_workdir + inputfile+ '.out', L_log + inputfile+ '.out')
                    else:
                        self.download(channel, tmp_workdir + lammpslog, L_log + lammpslog)
                        self.download(channel, tmp_workdir + inputfile+ '.out', L_log + inputfile+ '.out')

            else:
                self.download(channel, R_workdir + slurmerrorlog, L_log + slurmerrorlog)
                self.download(channel, R_workdir + slurmlog, L_log + slurmlog)
                self.download(channel, R_workdir + inputfile, L_log + inputfile + '_remote')
                self.download(channel, R_workdir + lammpslog, L_log + lammpslog)
                self.download(channel, R_workdir + inputfile+ '.out', L_log + inputfile+ '.out')
            
        if plotlog_local == 1:
            with open(L_log + logfile, encoding="utf8", errors='ignore') as log:
                lmplog = log.readlines()
            print(L_log + logfile)
        else:
            log = ftp.open(R_workdir + logfile)
            lmplog = log.readlines()
        wflag = False
        isdata = False
        newline = []
        result = []
        counter = 0
        index = 'X'
        replica = []

        for line in lmplog:  # 按行读入文件，此时line的type是str
            if line.startswith("Loop"):  # 重置写标记
                wflag = False
                isdata = False
                index = 'X'
            if "Step" in line:  # 检验是否到了要写入的内容
                counter += 1
                check0 = counter
                wflag = True
                result = [[j] for j in line.split()]
                NU_param = len(line.split())
                title = line.split()
                index = 0
                # isdata == False
                continue
            if wflag == True:
                # print(index)
                check = counter
                index += 1
                if index == 2:  ## 设置为1则从第一行开始，设置为2则从第二行数据开始，但有点小问题，会缺少一些数据
                    isdata = True
            if isdata == True and index != 'X' and check == check0:
                if "ERROR" not in line and 'Last c' not in line and 'WARNING:' not in line:
                    # print(line)
                    if line.split()[0].isnumeric and len(line.split()) == NU_param:  ## 防止数据还未生成完全的row被加入结果
                        newline.append(line)
                        ### remove replica ####
                        # if line not in newline:
                        #     newline.append(line)
                        # else:
                        #     replica.append(line)
                    else:
                        print('Found incomplete line:', line)
        alllines = []
        for line in newline:
            linetolist = line.split()
            alllines.append(linetolist)
            for ncol in range(len(linetolist)):
                result[ncol].append(linetolist[ncol])

        float_result = []
        print('ncols: ', len(result))
        for i in result:
            # print(i)
            i.pop(0)  ## 去除i list的第一个数据 title
            i = list(np.float_(i))  ## 转换剩余数据为np array
            float_result.append(i)
        print('loop: ', counter)  ## loop数目
        
        try:
            with open(L_log + '0Thermodata_log.txt', 'w') as handle:
                handle.write('\t'.join(title) + '\n')
                # handle.writelines('\t'.join(newline.split()) + '\n')
                for line in alllines:
                    handle.writelines('\t'.join(line) + '\n')

            if replica != []:
                with open(L_log + '0replica.txt', 'w') as handl:
                    handl.writelines(replica)

            taillammpslog = self.sendcommand(channel,out=0,command='tail '+R_workdir+lammpslog)
            jobsucceed = False
            for i in taillammpslog:
                if 'All done' in taillammpslog or 'Total wall time' in i:
                    # print(taillammpslog)
                    jobsucceed = True
                    if i.startswith('Total wall time'):
                        print(i)
                        time_str = i.split()[-1].split(':')
                        totaltime = int(time_str[0])*60*60 + round(int(time_str[1])*60) + round(int(time_str[2]))
                        print('Job already finished in',int(time_str[0]) + round(int(time_str[1])/60,2),'hours')
                        elapsedtime = totaltime

            # print('Progress:',progress + str(currentstep)+'/'+str(totalsteps))

            totalsteps = self.totalsteps() ### 并不完全准确？

            if jobsucceed: #  and totalsteps - currentstep <800
                currentstep = totalsteps
                progress = str(round(100.00,2)) + '% '
                predicted_time = 0.00
                bar_number = 50
            else:
                currentstep = int(float_result[0][-1])
                progress = str(round((currentstep/totalsteps)*100,2)) + '% '
                elapsedtime = self.times_job_elapsed() # Second
                predicted_time = (elapsedtime*totalsteps/currentstep - elapsedtime)/60/60
                print(elapsedtime*totalsteps/currentstep,elapsedtime)
                bar_number = int((currentstep/totalsteps)*100/2)
            ### display progress bar
            progressbar = list('|'+'-'*50+'|')
            for i in range(bar_number):
                progressbar[i+1] = '|'
            print('Progress:',progress+''.join(progressbar)+' '+str(currentstep)+'/'+str(totalsteps)+'  |'+str(round(predicted_time,2))+' hours left')

            dt = float(timestep)  ##  fs
            times = [i * dt / 1000 for i in float_result[0]]
            print('simulated frames (duplica results are includes): ',len(result[0]))
            print('simulated time: ',round(float(times[-1]),2),' ps')
            if plot:
                c_reaxdict = {'v_eb':'bond energy','v_ea':'atom energy','v_elp':'lone-pair energy','v_emol':'molecule energy (always 0.0)' ,'v_ev':'valence angle energy' ,'v_epen':'double-bond valence angle penalty','v_ecoa':'valence angle conjugation energy' ,'v_ehb':'hydrogen bond energy','v_et':'torsion energy' ,'v_eco':'conjugation energy','v_ew':'van der Waals energy','v_ep':'Coulomb energy','v_efi':'electric field energy (always 0.0)','v_eqeq':'charge equilibration energy'}
                c_reax = list(c_reaxdict.keys())

                for x_picked_col in [0, 1]:  ## xaxis数据源
                    fig = plt.figure(figsize=(18, 18), dpi=200)
                    for y_picked_col in range(0, len(float_result)):
                        if x_picked_col != y_picked_col:
                            subplotindex = y_picked_col
                            ax3 = fig.add_subplot(5, 6, 1 + subplotindex)
                            if x_picked_col == 0: ## turn step to time
                                ax3.plot(times[a:b:skip], float_result[y_picked_col][a:b:skip],
                                     label=title[y_picked_col])  ### 每隔10点取数据
                                if title[y_picked_col] in c_reax:
                                    ax3.set_title(c_reaxdict[title[y_picked_col]],fontsize=7)
                                # ax3.set_title('Fig. ' + str(subplotindex) + '  ' + title[y_picked_col] + ' VS. ' + 'time (ps)')
                                ax3.set_xlabel('time (ps)')
                            else:
                                ax3.plot(float_result[x_picked_col][a:b:skip], float_result[y_picked_col][a:b:skip],
                                     label=title[y_picked_col])  ### 每隔10点取数据
                                ax3.set_xlabel(title[x_picked_col])
                                if title[y_picked_col] in c_reax:
                                    ax3.set_title(c_reaxdict[title[y_picked_col]],fontsize=7)
                                # ax3.set_ylabel(title[y_picked_col])
                                # ax3.set_title('Fig. ' + str(subplotindex) + '  ' + title[y_picked_col] + ' VS. ' + title[x_picked_col])
                            ax3.legend()
                            # plt.subplots_adjust(top=2)
                            plt.subplots_adjust(hspace=0.5)
                        else:
                            print('skipping meaningless plot: ' + str(title[y_picked_col]) + ' vs. ' + str(title[y_picked_col]))
                    plt.show
        except:
            print('plot log failed, is there any data in 0Thermodata_log.txt?')
            
    def results_checker(self,ranges,columns=[0,1,5,6],plot=False): #20220612
        print('Using loacl 0Thermodata_log.txt')
        L_log = self.L_log
        dt = self.gettimestep()
        try:
            df = pd.read_csv(L_log + '0Thermodata_log.txt',sep = '\t')
        except:
            print('PLZ plotlog first')
            return 0
        df = df.drop_duplicates()
        
        # len(df["Step"].unique())
        # df.loc[df["Step"] == 100]
        # df.plot(df.columns[0],df.columns[1])
        # df.plot(df.columns[0],df.columns[2])
        # df.columns
        # use interact decorator to decorate the function, so the function can receive the slide bar's value with parameter x
        
        if ranges != (0,0):
            i = ranges
        else:
            # i=(0,max(df[df.columns[0]])-1)
            max_i = len(df[[df.columns[0]]]['Step'])-1
            i = (0,max_i)
        @interact(i=i)
        def rresults_checker(i):
            for k in columns:
                if k == 0:
                    locals()[df.columns[k]] = df[df.columns[k]][i]*float(dt)
                    print('Current step: %d time: %d fs.' % (df[df.columns[k]][i], locals()[df.columns[k]]))
                else:
                    locals()[df.columns[k]] = df[df.columns[k]][i]
                    print("        %s: %d." % (df.columns[k],locals()[df.columns[k]]))
        if plot:
            size = int(math.sqrt(len(columns)))+1
            fig = plt.figure(figsize=(10, 10), dpi=130)
            for k in range(len(columns)):
                ax = fig.add_subplot(size, size, 1+k)
                ax.plot(df['Step']*float(dt)/1000,df[df.columns[k]],label=df.columns[k])
                ax.set_xlabel('time (ps)')
            ax.legend()
            plt.show
        return df
    
    def trajviewer(self, refresh=1, viewangle='Half', write='pdb', frame=[0],info=True):
        
        channel = self.channel
        slurmerrorlog = self.slurmerrorlog
        L_log = self.L_log
        inputfile = self.inputfile
        lammpslog = self.lammpslog
        slurmlog = self.slurmlog
        ftp = self.ftp
        L_traj = self.L_traj
        trajs = self.trajs
        L_workdir = self.L_workdir
        
        getlmpdatafile = self.getlmpdatafile()
        a_topo = L_traj + getlmpdatafile
        a_trj = L_traj + trajs
        
        R_workdir=''
        if self.node=='jupyter':
            tmp_workdir='/tmp/'+'lym@'+self.current_job_id()+'/'
            if 'null' not in tmp_workdir: ## means job is running
                R_workdir=tmp_workdir
            else:
                tmp_workdir = self.previous_working_dir
                print('downloading from previous_working_dir, testing...')
                output=self.download(channel, tmp_workdir + inputfile, L_log + inputfile + '_remote')
                if 'failed' in output:
                    print('previous_working_dir doesnt exist, downloading from R_workdir')
                    self.download(channel, R_workdir + inputfile, L_log + inputfile + '_remote')
                    R_workdir= self.R_workdir
                else:
                    R_workdir=tmp_workdir
            
        if refresh != 1 and info:
            print('-----------------------------------------------------------------------------------------')
            print('Visualling local traj file! PLZ ensure that the data you are using is the latest version')
            print('------------------------- latest version on server -------------------------------')
            print(self.sendcommand(channel, 0, 'ls -lh ' + R_workdir + trajs))
            print('--------------------------  version of local files--------------------------------')
            print(self.listlocallogfile(L_traj + trajs))
            if not os.path.isfile(L_traj + trajs):
                    self.download(channel, R_workdir + trajs, L_traj + trajs)
            if not os.path.isfile(L_traj + getlmpdatafile):
                    self.download(channel, R_workdir + getlmpdatafile, L_traj + getlmpdatafile)
        
        remotefiles = ftp.listdir(R_workdir)  
        
        for i in range(len(remotefiles)):
            # print(remotefiles)
            if trajs == remotefiles[i]:
                if refresh == 1:
                    # print( R_workdir + remotefiles[i], L_traj + remotefiles[i])
                    self.download(channel, R_workdir + remotefiles[i], L_traj + remotefiles[i])
            if getlmpdatafile == remotefiles[i]:
                if refresh == 1:
                    # print(R_workdir + remotefiles[i], L_traj + remotefiles[i])
                    self.download(channel, R_workdir + remotefiles[i], L_traj + remotefiles[i])
                    
        if info:
            print('topo|trajs: ', getlmpdatafile, '|', trajs)
        topo_format = 'DATA'
        trj_format = 'LAMMPS'
        a_lengthunit = "A"
        a_timeunit = "fs"
        a_atom_style = 'id type charge x y z'  ##  Only when use lammps data as topo. Required fields: id, resid, x, y, z  Optional fields: resid, charge

        if a_atom_style != '':
            # print('using lammps data file')
            print(a_topo, a_trj)
            u = mda.Universe(a_topo, a_trj, topology_format=topo_format, format=trj_format,
                             atom_style=a_atom_style, lengthunit=a_lengthunit, timeunit=a_timeunit)
        else:
            u = mda.Universe(a_topo, a_trj, topology_format=topo_format, format=trj_format,
                             lengthunit=a_lengthunit, timeunit=a_timeunit)
        if info:
            print(u.kwargs)

        u.add_TopologyAttr('resname', [''] * len(u.segments.residues))
        u.add_TopologyAttr('names', range(len(u.atoms)))
        u.add_TopologyAttr('chainID')  ###
        
        atom_types = ['Al','O','Al','O','H','O']
        chainIDs = ['A','B','C','D','E','F']
        for i in range(len(atom_types)):
            u.select_atoms('type  '+str(i+1)).names = [atom_types[i]]*len(u.select_atoms('type  '+str(i+1)))
            u.select_atoms('type  '+str(i+1)).chainIDs = chainIDs[i]
        
        #### indexing
        type1index = u.select_atoms('type  1').indices
        type2index = u.select_atoms('type  2').indices
        type3index = u.select_atoms('type  3').indices
        type4index = u.select_atoms('type  4').indices
        type5index = u.select_atoms('type  5').indices
        type6index = u.select_atoms('type  6').indices
        index = [type1index,type2index,type3index,type4index,type5index,type6index]
        
        ### indexing half by atom index
        halfindex = []
        for i in range(len(index)):
            if len(index[i]) > 0:
                locals()['half'+str(i)] = [str(index[i][0]),str(int(int(index[i][-1]-index[i][0])/2)+int(index[i][0]))]
                halfindex.append(locals()['half'+str(i)])
        
        ### check and create indices file
        if not os.path.isfile(L_workdir + self.PJname+'_half_index.txt'):
            ## all 
            atoms = u.select_atoms('all')
            allatom_indexs = atoms.atoms.indices

            ### half by geo
            atoms = u.select_atoms('all')
            for i in range(len(atoms)):
                if atoms[i].position[0] > 0:
                    atoms[i].residue = u.add_Residue(segment=u.segments[0], resid=1, resname='cf',
                                                     resnum=1)  # clusterResidue
            atoms = u.select_atoms('resname cf')
            half_atom_indexs = atoms.atoms.indices ### half index by geometry 

            ## half by atom index
            selections = []
            for i in halfindex:
                selection_i = ' or index '+i[0]+':'+i[1]
                selections.append(selection_i)
            selcetions = ''.join(selections)
            select_string = selcetions.replace(selcetions[0:3], '', 1)
            # print(select_string)
            atoms = u.select_atoms(select_string)
            half_by_indexs = atoms.atoms.indices # ## half index by atom index 

            with open(L_workdir + self.PJname+'_half_index.txt', 'w') as file_list:
                file_list.write('### half index by geometry \n')
                file_list.write(str(half_atom_indexs.tolist())+'\n')
                file_list.write('## half index by atom index \n')
                file_list.write(str(half_by_indexs.tolist())+'\n')
                file_list.write('## all atom index \n')
                file_list.write(str(allatom_indexs.tolist())+'\n')
                
        with open(L_workdir + self.PJname+'_half_index.txt', 'r') as file_list:
                    k = file_list.readlines()
                    half_atom_indexs,half_by_indexs,allatom_indexs = k[1].split(','),k[3].split(','),k[5].split(',')
                    atom_indexs = [half_atom_indexs,half_by_indexs,allatom_indexs]
                    atom_indexs_all = []
                    for j in range(3):
                        atom_indexs_i = []
                        for i in atom_indexs[j]:
                            i=i.strip('[')
                            i=i.strip(']\n')
                            atom_indexs_i.append(i)
                        atom_indexs_all.append(atom_indexs_i)
                        
        if viewangle == 'All':
            atoms = u.select_atoms('all')
            if info:
                print('atoms: ', len(atoms.select_atoms('all')))
                print(atoms.dimensions)
            vvv = nv.show_mdanalysis(u.select_atoms('all'))
            if write != 0:
                for t in frame:
                    u.trajectory[t]
                    atoms.write(L_traj + inputfile + '-All-f-' + str(t) + '.' + write)
                    if info:
                        print('Writting file to: ', L_traj + inputfile + '-All-f-' + str(t) + '.' + write)
        elif viewangle == 'Half_byindex':
            ## deal with selection string 
            atomindex = ' '.join(atom_indexs_all[1]).strip(']\n').strip('[').split()
            atoms = 0
            for i in atomindex:
                atoms += u.select_atoms('index '+str(int(i)))
            if info:
                print(len(atoms))
                print(atoms.dimensions)
            vvv = nv.show_mdanalysis(atoms)
            if write != 0:
                for t in frame:
                    u.trajectory[t]
                    atoms.write(L_traj + inputfile + '-Half-f-' + str(t) + '.' + write)
                    print('Writting file to: ', L_traj + inputfile + '-Half-f-' + str(t) + '.' + write)
                    
        elif viewangle == 'Half':
            atomindex = ' '.join(atom_indexs_all[0]).strip(']\n').strip('[').split()
            atoms = 0
            for i in atomindex:
                atoms += u.select_atoms('index '+str(int(i)))
            vvv = nv.show_mdanalysis(atoms)
            if write != 0:
                for t in frame:
                    u.trajectory[t]
                    atoms.write(L_traj + inputfile + '-Half-f-' + str(t) + '.' + write)
                    print('Writting file to: ', L_traj + inputfile + '-Half-f-' + str(t) + '.' + write)
        else:
            print('error: trajviewer(viewangle Half/All/Half_byindex,write="pdb",frame=0):')
            vvv = 0
            atoms = u.select_atoms('all')
            
        MDAobject = [u,atoms]
        vvv.player.parameters = dict(delay=0.004, step=-1)
        # vw.background = 'black'
        return vvv,index,halfindex,MDAobject,atom_indexs_all
    
    def construct_sub_universe(self,u,selection = "type 1 2",singleframe=None):
        select = u.select_atoms(selection)
        
        print('Atoms in sub_universe:',len(select.atoms))
        coordinates = AnalysisFromFunction(lambda ag: ag.positions.copy(),
                                           select).run().results['timeseries']
        u2 = mda.Merge(select)            # create the protein-only Universe
        if singleframe!=None:
            print('All frames:',len(u.universe.trajectory),'Selected frame:',singleframe)
            print('singleframe')
            u2.load_new(coordinates[singleframe], format=MemoryReader)
        else:
            print('All frames:',len(u.universe.trajectory))
            u2.load_new(coordinates, format=MemoryReader)
        return u2

    def import_to_mda(self,topo,trj,atom_types,chainIDs,dt=0,topo_format = 'DATA',trj_format = 'LAMMPS',in_memory=True,in_memory_step=100):
        ########### also can use ##########
        ## u.transfer_to_memory(step=10) ##
        ###################################
        a_lengthunit="A"
        a_timeunit="fs"
        a_atom_style='id type charge x y z'  ##  Only when use data as topo format. Required fields: id, resid, x, y, z  Optional fields: resid, charge

        if dt!=0:
            print('Using self_defined dt (time between two frame in dump file)!!!!! Disable by setting dt = 0')
            arggs = {'dt':dt/1000}
        else:
            arggs = {}

        if topo_format == 'DATA':
            u = mda.Universe(topo,trj,topology_format = topo_format,format=trj_format, 
                             atom_style=a_atom_style,lengthunit=a_lengthunit, timeunit=a_timeunit,in_memory=in_memory,in_memory_step=in_memory_step,**arggs)      

        elif topo_format != 'DATA':
            u = mda.Universe(topo,trj,topology_format = topo_format,format=trj_format, 
                             lengthunit=a_lengthunit, timeunit=a_timeunit,in_memory=in_memory,in_memory_step=in_memory_step,**arggs)

        u.add_TopologyAttr('resname', ['']*len(u.segments.residues))
        u.add_TopologyAttr('names',range(len(u.atoms)))
        u.add_TopologyAttr('chainID')

        for i in range(4):
            u.select_atoms('type  '+str(i+1)).names = [atom_types[i]]*len(u.select_atoms('type  '+str(i+1)))
            u.select_atoms('type  '+str(i+1)).chainIDs = chainIDs[i]
        print(u.kwargs)
        print(len(u.trajectory),' frames')
        print(u.trajectory.dt,' dt (ps) for two frames')
        return u
    
    def cut_a_singleframe(self,u,frame,topo,trj,atom_types,chainIDs,dt=0,topo_format = 'DATA',trj_format = 'LAMMPS'):
        system = u.select_atoms('all')
        system.universe.trajectory[frame]
        totalframe= len(u.trajectory)
        currentframe = system.universe.trajectory.frame
        print('totalframe:',totalframe)
        print('selectedframe:',currentframe)
        system.write('/tmp/temp.dcd')
        # system.write('/tmp/temp.pdb')
        trj = '/tmp/temp.dcd'
        usingle = self.import_to_mda(topo,trj,atom_types,chainIDs,dt=0,topo_format = 'DATA',trj_format = 'LAMMPS',in_memory=False,in_memory_step=1)
        u = usingle
        return usingle
    
    def addpresentation(self,vw,style='ball+stick'):
        vw.clear()
        vw.clear_representations()
        atom_selections = ''
        if style == '':
            style='ball+stick'
        vw.add_representation(style, colorScheme='element', radiusType='size',multibond='symmetric')
        vw.add_representation('spacefill', selection=':A' + atom_selections, color='silver', radius='0.8')  ### atom name: .CA, .C, .N  element name: _H, _C, _O, chain name: :A
        vw.add_representation('spacefill', selection=':B' + atom_selections, color='red', radius='0.8')  ### atom name: .CA, .C, .N  element name: _H, _C, _O, chain name: :A
        vw.add_representation('spacefill', selection=':C' + atom_selections, color='black', radius='0.8')  ### atom name: .CA, .C, .N  element name: _H, _C, _O, chain name: :A
        vw.add_representation('spacefill', selection=':D' + atom_selections, color='yellow', radius='0.8')  ### atom name: .CA, .C, .N  element name: _H, _C, _O, chain name: :A
        vw.add_representation('spacefill', selection=':E' + atom_selections, color='grey', radius='0.6')  ### atom name: .CA, .C, .N  element name: _H, _C, _O, chain name: :A
        vw.add_representation('spacefill', selection=':F' + atom_selections, color='pink', radius='0.8')  ### atom name: .CA, .C, .N  element name: _H, _C, _O, chain name: :A
        vw.player.parameters = dict(delay=0.004, step=-1)
        # vw.background = 'black'
        return vw
    
    def nv_add_representation(self,vw,atom_indexs,viewangle='Half'):
        '''
        viewangle='Half All Half_byindex'
        '''
        T0 = time.time()
        #vw,index,halfindex,MDaObject,atom_indexs= self.trajviewer(refresh=0,viewangle='All',write=0,frame=[0,100,500,1000,49220],info = False)
        T1 = time.time()
        print('Half:',len(atom_indexs[0]),'Half_byindex:',len(atom_indexs[1]),'All:',len(atom_indexs[2]))
        if viewangle=='Half':
            atomindex = atom_indexs[0]
        if viewangle=='All':
            atomindex = atom_indexs[2]
        if viewangle=='Half_byindex':
            atomindex = atom_indexs[1]
        startT = time.time()
        vw.clear()
        vw.clear_representations()
        selected_atomindex=[str(i) for i in atomindex]
        atom_selections =  ' and '+'@'+','.join(selected_atomindex)
        atom_selections = atom_selections.replace(', ',',')
        # print(':D' + atom_selections)
        T2 = time.time()
        vw.add_representation('ball')
        vw.add_representation('spacefill', selection=':A' + atom_selections, color='silver', radius='0.8')  ### atom name: .CA, .C, .N  element name: _H, _C, _O, chain name: :A
        vw.add_representation('spacefill', selection=':B' + atom_selections, color='red', radius='0.8')  ### atom name: .CA, .C, .N  element name: _H, _C, _O, chain name: :A
        vw.add_representation('spacefill', selection=':C' + atom_selections, color='black', radius='0.8')  ### atom name: .CA, .C, .N  element name: _H, _C, _O, chain name: :A
        vw.add_representation('spacefill', selection=':D' + atom_selections, color='yellow', radius='0.8')  ### atom name: .CA, .C, .N  element name: _H, _C, _O, chain name: :A
        vw.add_representation('spacefill', selection=':E' + atom_selections, color='grey', radius='0.6')  ### atom name: .CA, .C, .N  element name: _H, _C, _O, chain name: :A
        vw.add_representation('spacefill', selection=':F' + atom_selections, color='pink', radius='0.8')  ### atom name: .CA, .C, .N  element name: _H, _C, _O, chain name: :A
        T3 = time.time()
        vw.player.parameters = dict(delay=0.004, step=-1)
        # vw.background = 'black'
        
        
        print(T1 - T0)
        print(T2 - T1)
        print(T3 - T2)
        print(T3 - T0)
        return vw
        # # vw.add_representation('spacefill', selection='.Al and '+ atom_selections, color='white', radius='1')  ### atom name: .CA, .C, .N  element name: _H, _C, _O,  
        # vw.add_representation('line', selection= atom_selections, color='green', radius='0.5',opacity=0.8)
        # vw.add_representation('licorice', selection= atom_selections, color='green', radius='0.5',opacity=0.8)
        # vw.add_representation('label', labelType = 'text',labelText = 'hhhh',selection= atom_selections, color='green',zOffset=2.0, attachment='middle_center')
        # vw.add_unitcell()

        #Ehttps://nglviewer.org/ngl/api/manual/selection-language.html
        # import ase
        # import ase.io
        # from ase.visualize import view
        # for i in [0,100,500,1000,49220]:
        #     d = ase.io.read(L_traj+'in.input-Half-f-'+str(i)+'.xyz')
        #     v = nv.show_ase(d)
        
        
    #  GET NODE INFO FROM UNAME -A-------------------------------------------------------------------------------------
    def current_login_Node(self, out):
        channel = self.channel

        k = self.sendcommand(channel, 0, 'uname -a')
        results0 = k[0].split()
        d = self.sendcommand(channel, 0, 'date')
        results = d[0].split()
        date = '-'.join([results[0], results[3], results[1], results[2]])
        ccc = results0[1], date
        if out == 1:
            print('Current_login_Node: ', ccc)
        return ccc

    ## slurm ---------------------------------------------------------------------------------------------------------
    
    def times_job_elapsed(self):
        taillammpslog = self.sendcommand(self.channel,out=0,command='tail '+self.R_workdir+self.lammpslog)
        jobsucceed = False
        for i in taillammpslog:
            if 'All done' in taillammpslog or 'Total wall time' in i:
                jobsucceed = True
                if i.startswith('Total wall time'):
                    time_str = i.split()[-1].split(':')
                    totaltime = int(time_str[0])*60*60 + round(int(time_str[1])*60) + round(int(time_str[2]))
                    print('Job already finished in',int(time_str[0]) + round(int(time_str[1])/60,2),'hours')
                    elapsedtime = totaltime
        # print('Progress:',progress + str(currentstep)+'/'+str(totalsteps))
        if not jobsucceed:
            print('Job is not done yet, tring to obtain info from slurm')
            jobids,jobnames,jobstat,elapsedtimes,nodelists = self.sendcommand(self.channel,out=0,command='squeue')[-1]
            # print(jobids,jobnames,jobstat,elapsedtimes,nodelists)
            total_times = []
            for i in elapsedtimes:
                # print(i)
                if '-' in i:
                    time_strs = []
                    d = int(i.split('-')[0]) ## extract days
                    # print(d)
                    time_strs.append(d)
                    for k in i.split('-')[1].split(':'):# extract time
                        time_strs.append(int(k))
                    T = time_strs
                    if len(time_strs) == 4:
                        total_time = T[0]*24*60*60 + T[1]*24*60 + T[2]*60 + T[3]
                    if len(time_strs) == 3: ##  1-3:00 1 day and 3 mins
                        T = time_strs
                        total_time = T[0]*24*60*60 + T[1]*60 + T[2]
                else:
                    time_strs = []
                    for k in i.split(':'):# extract time
                        time_strs.append(int(k))
                    T = time_strs
                    if len(time_strs) == 3:
                        total_time = T[0]*60*60 + T[1]*60 + T[2]
                    if len(time_strs) == 2: ##  1-3:00 1 day and 3 mins
                        T = time_strs
                        total_time = T[0]*60 + T[1]
                total_times.append(total_time)
            
            if self.node=='jupyter':
                currentnode = self.current_working_node()
            else:
                currentnode = self.current_login_Node(out=0)[0]
                
            if currentnode!='null':
                for i in range(len(nodelists)):
                    if nodelists[i] == currentnode and jobstat[i]=='R':
                        print('Current node info: ',jobids[i],jobnames[i],str(jobstat[i]),elapsedtimes[i],nodelists[i])
                        print('Elapsed_time/h :',round(total_times[i]/60/60,2))
                        elapsedtime = total_times[i]
                        if type(elapsedtime) != int:
                            elapsedtime = 0
            else:
                # print('job is not running!')
                elapsedtime=0

        return elapsedtime
                
    def scancel(self, x):
        channel = self.channel
        All_jobsID = self.sendcommand(channel, 0, 'squeue')[0]
        PD_jobsID = self.sendcommand(channel, 0, 'squeue')[1]
        R_jobsID = self.sendcommand(channel, 0, 'squeue')[2]
        if x == 'all':
            jobsID = All_jobsID
            end = len(jobsID)
            start = 0
            for i in range(start, end):
                self.sendcommand(channel, 0, 'scancel ' + jobsID[i])
        elif x == 'pending':
            jobsID = PD_jobsID
            end = len(jobsID)
            start = 0
            for i in range(start, end):
                self.sendcommand(channel, 0, 'scancel ' + jobsID[i])
        elif x == 'running':
            jobsID = R_jobsID
            end = len(jobsID)
            start = 0
            for i in range(start, end):
                self.sendcommand(channel, 0, 'scancel ' + jobsID[i])
        elif x.isnumeric():
            # print(x.type())
            rightinput = False
            for i in All_jobsID:
                if x == str(i):
                    self.sendcommand(channel, 0, 'scancel ' + str(x))
                    rightinput = True
                    break
            if not rightinput:
                print('usage: all/pending/jobnumber/running')
        else:
            print('usage: all/pending/jobnumber/running')

    def sinfo(self):
        channel = self.channel
        self.sendcommand(channel, 1, 'sinfo')

    def squeue(self,out=1):
        channel = self.channel
        results = self.sendcommand(channel, out, 'squeue --format="%.18i %.15P %.50j %.8u %.8T %.10M %.9l %.6D %R"')
        return results

    def current_working_node(self):
        jobinfos = self.squeue(out=0)
        ids = jobinfos[3][0]
        names = jobinfos[3][1]
        times = jobinfos[3][3]
        stats = jobinfos[3][2]
        nodes = jobinfos[3][4]

        current_job_id = 'null'
        node_for_job = 'null'
        for index,name in enumerate(names):
            if 'in.'+self.PJname == name:
                # print(self.PJname,name)
                current_job_id = ids[index]
                node_for_job = nodes[index]
                return node_for_job
                break
        else:
            print('node_for_job is null, is job still running?')
            return node_for_job
        
    def current_job_id(self):
        jobinfos = self.squeue(out=0)
        ids = jobinfos[3][0]
        names = jobinfos[3][1]
        times = jobinfos[3][3]
        stats = jobinfos[3][2]
        nodes = jobinfos[3][4]

        current_job_id = 'null'
        node_for_job = 'null'
        for index,name in enumerate(names):
            if 'in.'+self.PJname == name:
                # print(self.PJname,name)
                current_job_id = ids[index]
                node_for_job = nodes[index]
                return current_job_id
                break
        else:
            print('current_job_id is null, is job still running?')
            return current_job_id
        
    def current_job_info(self):
        jobinfos = self.squeue(out=0)
        ids = jobinfos[3][0]
        names = jobinfos[3][1]
        times = jobinfos[3][3]
        stats = jobinfos[3][2]
        nodes = jobinfos[3][4]
        currentnode = self.current_working_node()
        current_job_info = []
        for i in range(len(ids)):
            if currentnode == nodes[i] and stats[i] == 'R':
                current_job_info = [ids[i],names[i],times[i],stats[i]]
                break
            if currentnode == nodes[i] and stats[i] == 'PD':
                current_job_info = [ids[i],names[i],times[i],stats[i]]
                break
        if current_job_info == []:
            print('Job is not in R stat!')
            current_job_info = ['null','null','null','null']
        print('job_info:',current_job_info)
        return current_job_info
    

    def refresh_node_info(self,out=1):
        try:
            # 必须有，用于试错，防止文件直接被清空
            current_login_Node,current_date=self.current_login_Node(out=0)
            current_working_node=self.current_working_node()
            current_job_id=str(self.current_job_id())
            
            if out ==1:
                print('current_login_Node: '+current_login_Node)
                print('working_node: '+current_working_node)
                if current_working_node!='null':
                    print('tmp_working_dir: ','/tmp/'+'lym@'+current_job_id+'/')
                else:
                    print('will not change tmp_working_dir!')
            
            if current_working_node!='null':
                if current_login_Node!=current_working_node:
                    self.channel, self.ftp = self.select_channel(current_working_node)
                    if out ==1:
                        print('login node is differ from working node!\n!!!\n!!!\n!!!\n!!!')
                        print('trying to reset ssh channel!')
                        print('current_working_node:',current_working_node,'current_login_Node:',current_login_Node)
                        
                target = self.L_workdir + self.PJname + '_'+ self.node
                with open(target+'.txt', 'w') as W:
                    W.write(str(current_login_Node)+'\t'+str(current_date)+'\n')
                    W.write('working_node: '+current_working_node+'\n')
                    W.write('tmp_working_dir: '+'/tmp/'+'lym@'+current_job_id+'/'+'\n')
                    
                if '/tmp/'+'lym@'+current_job_id+'/'!=self.previous_working_dir:
                    self.previous_working_node=current_working_node
                    self.previous_working_dir='/tmp/'+'lym@'+current_job_id+'/'
                    if out ==1:
                        print('current_job_id is differ from previous job_id!')
                        print('trying to update job_id!')
            else:
                print('job is not running, keep previous landing info')

        except:
            print('Landing site remain unchanged')
            
    def submited_job_info(self,submission,sleep=5):
        for i in submission:
            if 'Submitted batch' in i:
                submited_job_id = i.split()[-1]
                print('submited_job_id',submited_job_id)
        print('checking job status')
        time.sleep(sleep)
        jobinfos = self.squeue(out=0)
        ids = jobinfos[3][0]
        names = jobinfos[3][1]
        times = jobinfos[3][3]
        stats = jobinfos[3][2]
        nodes = jobinfos[3][4]
        currentnode = self.current_login_Node(out=0)[0]
        current_job_info = []
        done = False
        print(ids)
        for i in range(len(ids)):
            print(ids[i])
            if str(ids[i]) == submited_job_id:
                current_job_info = [ids[i],names[i],times[i],stats[i],nodes[i]]
                done = True
                if 'RUNNI' in stats[i]:
                    print('Job is in stat:',stats[i])
                    print('Marvelous! seems that your script is working, go have some tea!\n'*3)
                    self.refresh_node_info()
                if 'P' in stats[i]:
                    print('Job is in stat:',stats[i])
                    print('Warning, youve submited a PD job..')
                    self.refresh_node_info()
                print('--------------------------------------------------------')
        if not done:
            print('Waring! Something bad happend!\n'*3)
            current_job_info = ['null','null','null','null']
        print('job_info:',current_job_info)
        print('--'*30)
        if not done:
            print('Checking slurmlog')
            self.checklog(refresh=1,Lastlog=4,Check_lammpslog=1,Check_slurmlog =1,Download_log=1,checklog_local=1)
        return current_job_info
            
    # -----------------------------------------------------------------------------------------------------------------
    # get info from previous file, but try to refresh first
    def previous_working_info(self):
        self.refresh_node_info(out=0)
        target = self.L_workdir + self.PJname + '_'+self.node
        with open(target+'.txt','r') as F:
            text = F.readlines()
            previous_working_node = text[1].split(' ')[-1].strip('\n')
            previous_working_dir = text[2].split(' ')[-1].strip('\n')
            return previous_working_node,previous_working_dir


    
    # htop ------------------------------------------------------------------------------------------------------------
    def top(self,out =1):
        channel = self.channel
        self.sendcommand(channel, 0, command='top -b -n1 > /tmp/top.out')
        toplog = self.sendcommand(channel, 0, command='head -c 380 /tmp/top.out  | tail -c +0')
        if out == 1:
            for i in toplog:
                print(i)
        return toplog

    # get info from local ----------------------------------------------------------------------------
    
    def gettimestep(self):
        L_input = self.L_input
        inputfile = self.inputfile

        with open(L_input + inputfile, encoding="utf8", errors='ignore') as inp:
            f = inp.readlines()
        fname = 0
        for i in f:
            if i.startswith('timestep'):
                fname = i.split()[-1]
        if fname == 0:
            print('Error, not found lmp file from local input')
        else:
            return fname

    def getlmpdatafile(self):
        L_input = self.L_input
        inputfile = self.inputfile
        fname=0
        with open(L_input + inputfile, encoding="utf8", errors='ignore') as inp:
            f = inp.readlines()
            for i in f:
                if i.startswith('read_data'):
                    fname = i.split()[-1]
                    return fname
                
        print('Error, not found lmp data file from reading local input file, auto-discovering lmp file')
        for file in os.listdir(L_input):
            if file.startswith('lmp'):
                fname=file
                print('found lmp data file',L_input+fname)
                return fname
            
        if fname==0:
            print('Error, no lmp data file found/detecd')

    def readlammpsdata(self,inputdata = 'lmp.S5.0--1_EM+Annealling.lmp',Mname = ['Al','O','Al']):
        print(f'visualizing {inputdata}')
        import mdapackmol
        import MDAnalysis as mda
        import nglview as nv
        F = open(inputdata)
        f =F.readlines()

        Positions = []
        Mmass = []
        dims = []

        for i in f:
            # print(i)
            x = i.split()
            if len(x) == 9 and x[0].isnumeric():

                ## lammps data file (charge)
                ## atom-ID atom-type q x y z
                posi = [x[0],x[1],str(float(x[3])),str(float(x[4])),str(float(x[5]))]
                # posi = [atom-ID atom-type x y z]
                # i = '\t'.join(posi) + '\n'
                # FF.append(i)
                Positions.append(posi)

            elif len(x) == 2 and x[0].isnumeric():
                try:
                    type(float(x[-1]))
                    Mmass.append(i.split()[1])
                    Matomtypes = int(x[0])
                except:
                    yyy=1

            elif len(x) == 4:
                if str(x[-1]).endswith('hi'): ## dimansion
                    i = i.strip('\n')
                    dims.append(i)
            else:
                yyy = 1
                
        if len(Positions)==0: ### 防止是vmd转换的data文件
            for i in f:
                x = i.split()
                if len(x) == 6 and x[0].isnumeric():
                    posi = [x[0],x[1],str(float(x[3])),str(float(x[4])),str(float(x[5]))]
                    Positions.append(posi)
        F.close()

        # print(Positions)
        print(f"Mmass {Mmass} \nMname:{Mname} \ndims:{dims} \nMatomtypes:{Matomtypes}")
        ## 将获取的atom 坐标信息按照原子id 从小到大排序
        ## posi = [atom-ID atom-type x y z]
        from natsort import natsorted
        Positions = natsorted(Positions)

        posi_types = []
        for i in range(Matomtypes):
            type_i_posi = []
            posi_types.append(type_i_posi)
            element = Mname[i]
            for k in Positions:
                if k[1] == str(i + 1):
                    k[1] = element ## 替换原子的type 为原子名称
                    k.pop(0) ## 删除atom id
                    type_i_posi.append(k) # k=[elements,x,y,z]
            posi_types[i] = type_i_posi

        New = '/tmp/xxxx.xyz'
        N = open(New,'w')
        N.write(str(len(Positions))+'\n\n')
        print('总原子数',len(Positions))
        ## 按原子顺序，依次写入 elements x y z到文件
        for index,type_i_posi in enumerate(posi_types):
            print('type',index,len(type_i_posi))
            for i in type_i_posi:
                N.write('  '.join(i) + '\n')
        N.close()

        ##### ensure the position is not out of boundary
        x = mda.Universe(New)

        ### determine boundry
        atoms = x.select_atoms('all')
        u = x
        from MDAnalysis.analysis import distances
        dist_arr = distances.distance_array(atoms.positions,atoms.centroid(),box=u.dimensions)
        print(f"共计算{len(dist_arr)}个原子距box center的距离，最小是{dist_arr.min()}，最大是{dist_arr.max()}")
        dist_arr_self = distances.self_distance_array(atoms.positions,box=u.dimensions)
        print(f"共计算{len(dist_arr_self)}对原子间距离，最小距离为{dist_arr_self.min()},最大距离为{dist_arr_self.max()}")
        vw = nv.show_mdanalysis(atoms)
        return vw
    # -----------------------------------------------------------------------------------------------------------------

    ### file and dirs 
    def R_workdirlist(self, sort='date'):
        R_workdir = self.R_workdir
        channel = self.channel
        x = self.sendcommand(channel, 0, 'ls -lh ' + R_workdir)
        info = []
        for i in x:
            x = i.split()
            if x[0] != 'total' and x[-1] != '.' and x[-1] != '..' and x[-1] != '...':
                if x[-5].isnumeric():
                    x[-5] += 'B'
                info.append('\t'.join([x[-5], x[-4] + '-' + x[-3] + '-' + x[-2], x[-1]]))
        if sort == 'name':
            info.sort(key=lambda k: k.split()[2])
        elif sort == 'size':
            info.sort(key=lambda k: k.split()[0])
        elif sort == 'date':
            info.sort(key=lambda k: k.split()[1])
        else:
            info = 0
            print('name size date')
        if info != 0:
            print(R_workdir)
            print('----------------------------------------------------------')
            for i in info:
                print(i)

    def list_L_and_R_files(self):
        L_folders = self.L_folders
        R_workdir = self.R_workdir
        L_foldernames = self.L_foldernames
        R_foldername = self.R_foldername
        ftp = self.ftp
        print('###########  Local workdir #############')
        for i in range(len(L_folders)):
            idir = os.listdir(L_folders[i])
            try:
                idir.remove('.ipynb_checkpoints')
            except:
                print(' ')
            idirindex = []
            for index, h in enumerate(idir):
                idirindex.append(str(index) + '. ' + h)
            print('|' + L_foldernames[i] + '|' + '\n' + '\t'.join(
                idirindex[0:]) + '\n--------------------------------------------------------------------------')
        # !tree /home/flare/MD-analysis/al_shell_3_1/
        print('###########  Remote workdir #############')
        idirR = ftp.listdir(R_workdir)
        try:
            idirR.remove('.ipynb_checkpoints')
        except:
            print(' ')
        idirindexR = []
        for index, h in enumerate(idirR):
            idirindexR.append(str(index) + '. ' + h)
        print('|' + R_foldername + '|' + '\n' + '\t'.join(
            idirindexR[0:]) + '\n--------------------------------------------------------------------------')

    def getuploadlists(self):
        L_workdir = self.L_workdir
        k = os.listdir(L_workdir + '#input')
        uploadlists = k
        try:
            uploadlists.remove('.ipynb_checkpoints')
        except:
            print(' ')
        # print('uploadlists: ',uploadlists)
        return uploadlists

    def getdownloadlists(self):
        R_workdir = self.R_workdir
        ftp = self.ftp
        counter = 0
        k = ftp.listdir(R_workdir)
        downloadlists = k[:]
        try:
            downloadlists.remove('.ipynb_checkpoints')
            counter += 1
        except:
            f = 1
        try:
            downloadlists.remove('.out')
            counter += 1
        except:
            f = 1
        # print('uploadlists: ',uploadlists)
        return downloadlists
    
    def listlocallogfile(self, target):
        command = ['ls', '-lh',target]
        with tempfile.TemporaryFile() as tempf:
            proc = subprocess.Popen(command, stdout=tempf)
            # proc = subprocess.Popen(['ls', '-lh', '/home/flare'], stdout=tempf)
            proc.wait()
            tempf.seek(0)
            # hh = tempf.read()
            content = tempf.read().decode('UTF-8')
        infos = content.splitlines(True)
        return infos




