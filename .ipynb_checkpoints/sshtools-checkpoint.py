import paramiko
import os


def select_channel(host):
    user = 'lym'
    password = "8566231jkl;'"
    port = 22
    route = '192.168.33.0/24'

    ip_seg = '.'.join(route.split('.')[:3]) + '.'  # 192.168.33.
    if host == 'pve':
        host = ip_seg + "2"
        user = 'root'
    elif host == 'jupyter':
        host = ip_seg + "5"
    elif host == 'x99':
        host = ip_seg + "11"
        user = 'flare'
    elif host == '5800x':
        host = ip_seg + "12"
        user = 'flare'
    elif 'node' in host:
        host = ip_seg + str(int(100 + int(host[4:])))
        # print(host)

    # print('## using ssh channel from jupyter_sshtools class')
    # print('host',host)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, port, user, password, timeout=10)
        ftp = ssh.open_sftp()
        channel = ssh
        return channel, ftp
    except:
        try:
            ssh.connect(host, port, user, '8566231jkl', timeout=10)
            ftp = ssh.open_sftp()
            channel = ssh
            return channel, ftp
        except:
            print('connetcing:', host, port, user)
            print('error, connect host, try: x99 / 5800x / jupyter / node[1-7]')


def sendcommand(channel, out, command='sinfo'):
    stdin, stdout, stderr = channel.exec_command(command)
    # stdout.channel.recv_exit_status()
    lines = stdout.readlines()
    if out == 1:
        for i in lines:
            print(i)
    if command == 'squeue' or command == 'squeue --format="%.18i %.15P %.50j %.8u %.8T %.10M %.9l %.6D %R"':
        All_jobsID = []
        names = []
        times = []
        nodelist = []
        PD_jobsID = []
        R_jobsID = []
        status = []
        # ['337', 'arch', 'in.input', 'flare', 'R', '0:03', '1', 'flare-5800x']
        for x in range(1, len(lines)):
            # print(lines[x].split())
            All_jobsID.append(lines[x].split()[0])
            names.append(lines[x].split()[2])
            status.append(lines[x].split()[4])
            times.append(lines[x].split()[5])
            nodelist.append(lines[x].split()[-1])

            if lines[x].split()[4] == 'PD':
                PD_jobsID.append(lines[x].split()[0])
            if lines[x].split()[4] == 'R':
                R_jobsID.append(lines[x].split()[0])
        All_jobsIDwithoutsort = All_jobsID.copy()
        extrainfos = [All_jobsIDwithoutsort, names, status, times, nodelist]
        All_jobsID.sort()
        PD_jobsID.sort()
        R_jobsID.sort()
        ensemble = [All_jobsID, PD_jobsID, R_jobsID, extrainfos]
        return ensemble
    else:
        return lines


def upload(channel, ftp, local_path, server_path):
    node = sendcommand(channel, out=0, command='echo $HOSTNAME')[0].strip('\n')
    filename = server_path.rsplit('/', 1)[-1]
    dir = server_path.replace(filename, '')
    try:
        ftp.mkdir(dir)
    except IOError:
        print("uploding via " + node, local_path)
    ftp.put(local_path, server_path)


def download(channel, ftp, server_path, local_path):
    node = sendcommand(channel, out=0, command='echo $HOSTNAME')[0].strip('\n')
    if '/' in local_path:
        filename = local_path.rsplit('/', 1)[-1]
        dir = local_path.replace(filename, '')
        try:
            os.mkdir(dir)
        except IOError:
            print("downloading via " + node, server_path)
    try:
        ftp.get(server_path, local_path)
        return 'download succeed'
    except:
        print('failed: ', server_path, local_path)
        return 'download failed'
