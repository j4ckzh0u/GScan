# coding:utf-8
import os, optparse, time, sys
from common import *


# 分析主机文件类异常
# 1、判断系统文件完整性
# 2、临时目录文件扫描
# 3、可疑隐藏文件扫描

class File_Analysis:
    def __init__(self):
        # 恶意文件列表
        self.file_malware = []
        # 恶意特征列表
        self.malware_infos = []
        # 获取恶意特征信息
        self.get_malware_info()
        # 系统完整性检测
        # self.check_system_integrity()
        # 临时目录文件扫描
        # self.check_tmp()
        # 可疑隐藏文件扫描
        # self.check_hide()

    # 检查系统文件完整性
    def check_system_integrity(self):
        suspicious = False
        malice = False
        system_file = ["depmod", "fsck", "fuser", "ifconfig", "ifdown", "ifup", "init", "insmod", "ip", "lsmod",
                       "modinfo", "modprobe", "nologin", "rmmod", "route", "rsyslogd", "runlevel", "sulogin", "sysctl",
                       "awk", "basename", "bash", "cat", "chmod", "chown", "cp", "cut", "date", "df", "dmesg", "echo",
                       "egrep", "env", "fgrep", "find", "grep", "kill", "logger", "login", "ls", "mail", "mktemp",
                       "more", "mount", "mv", "netstat", "ping", "ps", "pwd", "readlink", "rpm", "sed", "sh", "sort",
                       "su", "touch", "uname", "gawk", "mailx", "adduser", "chroot", "groupadd", "groupdel", "groupmod",
                       "grpck", "lsof", "pwck", "sestatus", "sshd", "useradd", "userdel", "usermod", "vipw", "chattr",
                       "curl", "diff", "dirname", "du", "file", "groups", "head", "id", "ipcs", "killall", "last",
                       "lastlog", "ldd", "less", "lsattr", "md5sum", "newgrp", "passwd", "perl", "pgrep", "pkill",
                       "pstree", "runcon", "sha1sum", "sha224sum", "sha256sum", "sha384sum", "sha512sum", "size", "ssh",
                       "stat", "strace", "strings", "sudo", "tail", "test", "top", "tr", "uniq", "users", "vmstat", "w",
                       "watch", "wc", "wget", "whereis", "which", "who", "whoami"]

        binary_list = ['/bin/', '/sbin/', '/usr/bin/', '/usr/sbin/', '/usr/local/sbin/', '/usr/local/bin/']
        for dir in binary_list:
            for file in os.listdir(dir):
                fpath = os.path.join('%s%s' % (dir, file))
                infos = os.popen("rpm -qf %s" % fpath).read().splitlines()
                if 'is not owned by any package' in infos[0]:
                    if file in system_file:
                        self.file_malware.append(
                            {u'异常类型': u'文件完整性检测', u'可疑信息': infos[0], u'文件路径': fpath,
                             u'排查方式': u'[1]rpm -qa %s [2]strings %s' % (fpath, fpath)})
                        suspicious = True
                    else:
                        malware = self.analysis_file(fpath)
                        if malware:
                            self.file_malware.append(
                                {u'异常类型': u'文件恶意特征', u'文件路径': fpath, u'恶意特征': malware,
                                 u'排查方式': u'[1]rpm -qa %s [2]strings %s' % (fpath, fpath)})
                            malice = True
        return suspicious, malice

    # 检查所有临时目录文件
    def check_tmp(self):
        suspicious = False
        malice = False
        tmp_list = ['/tmp/', '/var/tmp/', '/dev/shm/']
        for dir in tmp_list:
            for file in os.listdir(dir):
                fpath = os.path.join('%s%s' % (dir, file))
                malware = self.analysis_file(fpath)
                if malware:
                    self.file_malware.append(
                        {u'异常类型': u'文件恶意特征', u'文件路径': fpath, u'恶意特征': malware,
                         u'排查方式': u'[1]rpm -qa %s [2]strings %s' % (fpath, fpath)})
                    malice = True
        return suspicious, malice

    # 可疑文件扫描
    def check_hide(self):
        suspicious = False
        malice = False
        infos = os.popen(
            'find / -name " *" -o -name ". *" -o -name "..." -o -name ".." -o -name "." -o -name " " -print | grep -v "No such" |grep -v "Permission denied"').read().splitlines()
        for file in infos:
            self.file_malware.append(
                {u'异常类型': u'文件异常隐藏', u'文件路径': file, u'排查方式': u'[1]ls -l %s [2]strings %s' % (file, file)})
            suspicious = True
        return suspicious, malice

    # 获取配置文件的恶意域名等信息
    def get_malware_info(self):
        if not os.path.exists('malware'): return
        for file in os.listdir('./malware/'):
            time.sleep(0.001)  # 防止cpu占用过大
            with open(os.path.join('%s%s' % ('./malware/', file))) as f:
                for line in f:
                    if len(line) > 3:
                        if line[0] != '#': self.malware_infos.append(line.strip().replace("\n", ""))

    # 分析文件是否包含恶意特征或者反弹shell问题
    def analysis_file(self, file):
        if not os.path.exists(file) or os.path.getsize(file) == 0: return ""
        strings = os.popen("strings %s" % file).readlines()
        for str in strings:
            if self.check_shell(str): return 'bash shell'
            for malware in self.malware_infos:
                if malware in str: return malware
        return ""

    # 分析字符串是否包含反弹shell特征
    def check_shell(self, content):
        return True if (('bash' in content) and (
                ('/dev/tcp/' in content) or ('telnet ' in content) or ('nc ' in content) or (
                'exec ' in content) or ('curl ' in content) or ('wget ' in content) or ('lynx ' in content))) or (
                               ".decode('base64')" in content) else False

    def run(self):
        print(u'\n开始文件类安全扫描')
        print align(u' [1]系统文件完整性安全扫描', 30) + u'[ ',
        file_write(u'\n开始文件类安全扫描\n')
        file_write(align(u' [1]系统文件完整性安全扫描', 30) + u'[ ')
        sys.stdout.flush()
        # 系统完整性检测
        suspicious, malice = self.check_system_integrity()
        if malice:
            pringf(u'存在风险', malice=True)
        elif suspicious and (not malice):
            pringf(u'警告', suspicious=True)
        else:
            pringf(u'OK', security=True)

        print align(u' [2]系统临时目录安全扫描', 30) + u'[ ',
        file_write(align(u' [2]系统临时目录安全扫描', 30) + u'[ ')
        sys.stdout.flush()
        # 临时目录文件扫描
        suspicious, malice = self.check_tmp()
        if malice:
            pringf(u'存在风险', malice=True)
        elif suspicious and (not malice):
            pringf(u'警告', suspicious=True)
        else:
            pringf(u'OK', security=True)

        print align(u' [3]可疑隐藏文件扫描', 30) + u'[ ',
        file_write(align(u' [3]可疑隐藏文件扫描', 30) + u'[ ')
        sys.stdout.flush()
        # 临时目录文件扫描
        suspicious, malice = self.check_hide()
        if malice:
            pringf(u'存在风险', malice=True)
        elif suspicious and (not malice):
            pringf(u'警告', suspicious=True)
        else:
            pringf(u'OK', security=True)
        sys.stdout.flush()

        if len(self.file_malware) > 0:
            file_write('-' * 30)
            file_write(u'文件检查异常如下：\n')
            for info in self.file_malware:
                file_write(json.dumps(info, ensure_ascii=False) + '\n')
            file_write('-' * 30)


if __name__ == '__main__':
    # File_Analysis().run()
    info = File_Analysis()
    info.run()
    print u"文件检查异常如下："
    for info in info.file_malware:
        print info