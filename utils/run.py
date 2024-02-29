import subprocess

class RunCommand:

    @staticmethod
    def execute_shell_wait(cmd):
        """
        execute shell with waiting to complete
        :return:
            (str) execute shell stdout
            (str) execute shell stderr
        """
        success = True
        cmd_args = cmd.split()
        result = subprocess.run(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode != 0:
            success = False

        return success, result.stdout.decode('utf-8'), result.stderr.decode('utf-8')

    @staticmethod
    def execute_shell_nowait(cmd):
        """
        execute shell with no wait to complete
        :param cmd:
        :return:
        """
        subprocess.Popen(cmd, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)

    @staticmethod
    def execute_bash_wait(cmd):
        """
        execute bash command line with waiting to complete
        :param cmd: (str) bash command
        :return:
        """
        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = ps.communicate()

        if stderr is not None:
            return False, stdout, stderr

        return True, stdout, stderr

    @staticmethod
    def execute_shell_wait_with_cmd_args(cmd_args):
        """
        execute shell with waiting to complete
        :return:
            (str) execute shell stdout
            (str) execute shell stderr
        """
        success = True
        result = subprocess.run(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode != 0:
            success = False

        return success, result.stdout.decode('utf-8'), result.stderr.decode('utf-8')