import os


def gen_sbatch_scripts(partition='Nebula_Elites', nodelist=None, nodes=1, ntasks_per_node=16, cpus_per_task=2, lammpsVersion=None,
                       mail=None, files='', comments='', singularity=False):
    print('Generating sbatch scripts for', partition)
    tmpsh = '/tmp/lammps_' + partition + '.sh'

    # when num_nodes = 1, tmp files should be stored in /tmp for best I/O performance
    if nodes == 1:
        if not singularity:
            if lammpsVersion:
                lammpsVersion = lammpsVersion
            else:
                lammpsVersion = 'lammps20220817git'
            print('using lammps version:', lammpsVersion)
            if partition == 'xeon72_broadwell':
                arch = 'broadwell'
                lmp = '/mnt/softs/LAMMPS/' + lammpsVersion + '/build_' + arch + '/lmp'
                spackenv = str('spack load' +
                               ' gcc@12.1.0%gcc@9.4.0 arch=linux-ubuntu20.04-' + arch +
                               ' ffmpeg@4.4.1%gcc@9.4.0 arch=linux-ubuntu20.04-' + arch +
                               ' openmpi@4.1.4%gcc@9.4.0 arch=linux-ubuntu20.04-' + arch +
                               ' intel-mkl arch=linux-ubuntu20.04-' + arch +
                               '\n')

            elif partition == 'epyc128_zen':
                arch = 'zen'
                lmp = '/mnt/softs/LAMMPS/' + lammpsVersion + '/build_' + arch + '/lmp'
                spackenv = str('spack load' +
                               ' gcc@12.1.0%gcc@9.4.0 arch=linux-ubuntu20.04-' + arch +
                               ' ffmpeg@4.4.1%gcc@9.4.0 arch=linux-ubuntu20.04-' + arch +
                               ' openmpi@4.1.4%gcc@9.4.0 arch=linux-ubuntu20.04-' + arch +
                               ' fftw@3.3.10%gcc@9.4.0 arch=linux-ubuntu20.04-' + arch +
                               '\n')

            elif partition == 'epyc128_zen2':
                arch = 'zen2'
                lmp = '/mnt/softs/LAMMPS/' + lammpsVersion + '/build_' + arch + '/lmp'
                spackenv = str('spack load' +
                               ' gcc@12.1.0%gcc@9.4.0 arch=linux-ubuntu20.04-' + arch +
                               ' ffmpeg@4.4.1%gcc@9.4.0 arch=linux-ubuntu20.04-' + arch +
                               ' openmpi@4.1.4%gcc@9.4.0 arch=linux-ubuntu20.04-' + arch +
                               ' fftw@3.3.10%gcc@9.4.0 arch=linux-ubuntu20.04-' + arch +
                               '\n')

            elif partition == 'Nebula_Elites':
                arch = 'zen3'
                lmp = '/mnt/softs/LAMMPS/' + lammpsVersion + '/build_' + arch + '/lmp'

                arch = 'zen2'  # change to zen 2 cause Nebula32_zen3 has same env as epyc128_zen2
                spackenv = str('spack load' +
                               ' gcc@12.1.0%gcc@9.4.0 arch=linux-ubuntu20.04-' + arch +
                               ' ffmpeg@4.4.1%gcc@9.4.0 arch=linux-ubuntu20.04-' + arch +
                               ' openmpi@4.1.4%gcc@9.4.0 arch=linux-ubuntu20.04-' + arch +
                               ' fftw@3.3.10%gcc@9.4.0 arch=linux-ubuntu20.04-' + arch +
                               '\n')

            elif partition == 'flare_private':
                arch = 'zen3'
                lmp = '/mnt/softs/LAMMPS/' + lammpsVersion + '/build_' + arch + '/lmp'

                arch = 'zen2'  # change to zen 2 cause Nebula32_zen3 has same env as epyc128_zen2
                spackenv = str('spack load' +
                               ' gcc@12.1.0%gcc@9.4.0 arch=linux-ubuntu20.04-' + arch +
                               ' ffmpeg@4.4.1%gcc@9.4.0 arch=linux-ubuntu20.04-' + arch +
                               ' openmpi@4.1.4%gcc@9.4.0 arch=linux-ubuntu20.04-' + arch +
                               ' fftw@3.3.10%gcc@9.4.0 arch=linux-ubuntu20.04-' + arch +
                               '\n')
            else:
                print('partition not exist!')
            with open(tmpsh, 'w') as W:
                W.write('#!/bin/bash\n')
                W.write('#SBATCH --partition=' + partition + '\n')
                if nodelist:
                    W.write('#SBATCH --nodelist='+nodelist+'\n')
                W.write('#SBATCH --error="Error.%x"\n')
                W.write('#SBATCH --output="Output.%x"\n')
                W.write('#SBATCH -N 1\n')
                W.write('#SBATCH --ntasks-per-node=' + str(ntasks_per_node) + '\n')
                W.write('#SBATCH --cpus-per-task=' + str(cpus_per_task) + '\n')
                W.write('\n')

                W.write('job=${SLURM_JOB_NAME}\n')
                W.write('v_np=${SLURM_NTASKS_PER_NODE:-1}\n')
                W.write('v_t=${SLURM_CPUS_PER_TASK:-1}\n')
                W.write('\n')

                W.write('tmpdir=/tmp/$USER@$SLURM_JOB_ID\n')
                W.write('cp -r $SLURM_SUBMIT_DIR $tmpdir\n')
                W.write('\n')

                W.write('###  loging ###\n')
                W.write('echo "Job execution start: $(date)" >>  $tmpdir/$job.out\n')
                W.write('echo "Slurm Job ID is: ${SLURM_JOB_ID}" >>  $tmpdir/$job.out\n')
                W.write('echo "Slurm Job name is: ${SLURM_JOB_NAME}" >>  $tmpdir/$job.out\n')
                W.write('echo "# of MPI processor,v_np is: ${SLURM_NTASKS_PER_NODE:-1}"  >>  $tmpdir/$job.out\n')
                W.write('echo "# of openMP thread, v_t is: ${v_t}" >>  $tmpdir/$job.out\n')
                W.write('\n')

                W.write('### set environment ###\n')
                W.write('. /mnt/softs/spack/share/spack/setup-env.sh\n')
                W.write('\n')

                W.write(spackenv)
                W.write('\n')

                W.write('#export OMP_NUM_THREADS=$v_t\n')
                W.write('#export OMP_PROC_BIND=false\n')
                W.write('#export OMP_PLACES=threads\n')
                W.write('\n')

                W.write('### run ###\n')
                W.write('cd $tmpdir\n')

                W.write(
                    'mpirun -np $v_np --display-map --map-by core --bind-to core --use-hwthread-cpus --map-by core -x OMP_PROC_BIND=True -x OMP_PLACES=cores -x OMP_NUM_THREADS=$v_t -x OMP_STACKSIZE=512m ' + lmp + ' -k on t $v_t -sf kk -in $job\n')
                W.write('\n')

                W.write('### loging and retrive outputs ###\n')
                W.write('echo "Job end: $(date) , retriving files" >>  $tmpdir/$job.out\n')
                W.write("###### rm not updating slurm logs before mv back outputs #####\n")
                W.write('rm -rf /tmp/$USER@$SLURM_JOB_ID/Error.* \n')
                W.write('rm -rf /tmp/$USER@$SLURM_JOB_ID/Output.* \n')
                W.write('mv /tmp/$USER@$SLURM_JOB_ID/* $SLURM_SUBMIT_DIR\n')
                W.write('echo "Job end: $(date)" >>  $tmpdir/$job.out\n')
                W.write('\n')

                if mail:
                    W.write('/mnt/softs/Scripts/mail.sh ' + mail + ' ' + files + ' ' + comments + '\n')
        # when num_nodes > 1, tmp files should be stored in shared storage
        else:
            print('using singularity')
            lmpsif='/mnt/softs/singularity_sifs/lmp_gnu_kokkos_omp_mpi_debain_jammy_stable_23Jun2022.sif'

            with open(tmpsh, 'w') as W:
                W.write('#!/bin/bash\n')
                W.write('#SBATCH --partition=' + partition + '\n')
                if nodelist:
                    W.write('#SBATCH --nodelist='+nodelist+'\n')

                W.write('#SBATCH --error="Error.%x"\n')
                W.write('#SBATCH --output="Output.%x"\n')
                W.write('#SBATCH --nodes='+str(nodes)+'\n')
                W.write('#SBATCH --ntasks-per-node=' + str(ntasks_per_node) + '\n')
                W.write('#SBATCH --cpus-per-task=' + str(cpus_per_task) + '\n')
                W.write('\n')

                W.write('job=${SLURM_JOB_NAME}\n')
                W.write('v_np=${SLURM_NTASKS_PER_NODE:-1}\n')
                W.write('v_t=${SLURM_CPUS_PER_TASK:-1}\n')
                W.write('\n')

                W.write('mkdir -p /tmp\n')
                W.write('tmpdir=/tmp/$USER@$SLURM_JOB_ID\n')
                W.write('cp -r $SLURM_SUBMIT_DIR $tmpdir\n')
                W.write('\n')

                W.write('###  loging ###\n')
                W.write('echo "Job execution start: $(date)" >>  $tmpdir/$job.out\n')
                W.write('echo "Slurm Job ID is: ${SLURM_JOB_ID}" >>  $tmpdir/$job.out\n')
                W.write('echo "Slurm Job name is: ${SLURM_JOB_NAME}" >>  $tmpdir/$job.out\n')
                W.write('echo "# of MPI processor,v_np is: ${SLURM_NTASKS_PER_NODE:-1}"  >>  $tmpdir/$job.out\n')
                W.write('echo "# of openMP thread, v_t is: ${v_t}" >>  $tmpdir/$job.out\n')
                W.write('\n')

                W.write('### run ###\n')
                W.write('cd $tmpdir\n')

                W.write('\n')
                W.write("srun --mpi=pmix \\")
                W.write('\n--cpu-bind=cores --cpus-per-task=$v_t \\')
                W.write('\n--export=ALL,OMPI_MCA_btl_tcp_if_include=192.168.33.0/24,OMP_PROC_BIND=True,OMP_PLACES=cores,OMP_NUM_THREADS=$v_t,OMP_STACKSIZE=512m \\')
                W.write('\nsingularity exec '+ lmpsif + ' lmp -k on t $v_t -sf kk -in $job')

                W.write('\n\n### loging and retrive outputs ###\n')
                W.write('echo "Job end: $(date) , retriving files" >>  $tmpdir/$job.out\n')
                W.write("###### rm not updating slurm logs before mv back outputs #####\n")
                W.write('rm -rf /tmp/$USER@$SLURM_JOB_ID/Error.* \n')
                W.write('rm -rf /tmp/$USER@$SLURM_JOB_ID/Output.* \n')
                W.write('mv /tmp/$USER@$SLURM_JOB_ID/* $SLURM_SUBMIT_DIR\n')
                W.write('echo "Job end: $(date)" >>  $tmpdir/$job.out\n')
                W.write('\n')

                if mail:
                    W.write('/mnt/softs/Scripts/mail.sh ' + mail + ' ' + files + ' ' + comments + '\n')


    else:
        #lmpsif='/mnt/softs/singularity_sifs/lmp_intel_hsw_kokkos_omp_mpi_ubuntu22_stable_23Jun2022'
        #lmpsif='/mnt/softs/singularity_sifs/lmp_gnu_kokkos_openmp_mpi_openmpi_vasp632.sif'
        lmpsif='/mnt/softs/singularity_sifs/lmp_gnu_kokkos_omp_mpi_debain_jammy_stable_23Jun2022.sif'

        with open(tmpsh, 'w') as W:
            W.write('#!/bin/bash\n')
            W.write('#SBATCH --partition=' + partition + '\n')
            if nodelist:
                W.write('#SBATCH --nodelist='+nodelist+'\n')

            W.write('#SBATCH --error="Error.%x"\n')
            W.write('#SBATCH --output="Output.%x"\n')
            W.write('#SBATCH --nodes='+str(nodes)+'\n')
            W.write('#SBATCH --ntasks-per-node=' + str(ntasks_per_node) + '\n')
            W.write('#SBATCH --cpus-per-task=' + str(cpus_per_task) + '\n')
            W.write('\n')

            W.write('job=${SLURM_JOB_NAME}\n')
            W.write('v_np=${SLURM_NTASKS_PER_NODE:-1}\n')
            W.write('v_t=${SLURM_CPUS_PER_TASK:-1}\n')
            W.write('\n')

            W.write('mkdir -p /home/lym/tmp\n')
            W.write('tmpdir=/home/lym/tmp/$USER@$SLURM_JOB_ID\n')
            W.write('cp -r $SLURM_SUBMIT_DIR $tmpdir\n')
            W.write('\n')

            W.write('###  loging ###\n')
            W.write('echo "Job execution start: $(date)" >>  $tmpdir/$job.out\n')
            W.write('echo "Slurm Job ID is: ${SLURM_JOB_ID}" >>  $tmpdir/$job.out\n')
            W.write('echo "Slurm Job name is: ${SLURM_JOB_NAME}" >>  $tmpdir/$job.out\n')
            W.write('echo "# of MPI processor,v_np is: ${SLURM_NTASKS_PER_NODE:-1}"  >>  $tmpdir/$job.out\n')
            W.write('echo "# of openMP thread, v_t is: ${v_t}" >>  $tmpdir/$job.out\n')
            W.write('\n')

            W.write('### run ###\n')
            W.write('cd $tmpdir\n')

            W.write('\n')
            W.write("srun --mpi=pmix \\")
            W.write('\n--cpu-bind=cores --cpus-per-task=$v_t \\')
            W.write('\n--export=ALL,OMPI_MCA_btl_tcp_if_include=192.168.33.0/24,OMP_PROC_BIND=True,OMP_PLACES=cores,OMP_NUM_THREADS=$v_t,OMP_STACKSIZE=512m \\')
            W.write('\nsingularity exec '+ lmpsif + ' lmp -k on t $v_t -sf kk -in $job')

            W.write('\n\n### loging and retrive outputs ###\n')
            W.write('echo "Job end: $(date) , retriving files" >>  $tmpdir/$job.out\n')
            W.write("###### rm not updating slurm logs before mv back outputs #####\n")
            W.write('rm -rf /home/lym/tmp/$USER@$SLURM_JOB_ID/Error.* \n')
            W.write('rm -rf /home/lym/tmp/$USER@$SLURM_JOB_ID/Output.* \n')
            W.write('mv /home/lym/tmp/$USER@$SLURM_JOB_ID/* $SLURM_SUBMIT_DIR\n')
            W.write('echo "Job end: $(date)" >>  $tmpdir/$job.out\n')
            W.write('\n')

            if mail:
                W.write('/mnt/softs/Scripts/mail.sh ' + mail + ' ' + files + ' ' + comments + '\n')

    os.system('chmod 777 ' + tmpsh)
    os.system('chmod u+x ' + tmpsh)
    print('gen_sbatch_scripts done')

    return tmpsh
