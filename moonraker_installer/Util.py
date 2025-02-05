import os
import subprocess
# pylint: disable=import-error # Only exists on linux
import pwd

from .Logging import Logger
from .Context import Context

class Util:

    # The systemd path where we expect to find moonraker service files
    # AND where we will put our service file.
    SystemdServiceFilePath = "/etc/systemd/system"

    # Returns the parent directory of the passed directory or file path.
    @staticmethod
    def GetParentDirectory(path):
        return os.path.abspath(os.path.join(path, os.pardir))


    # Runs a command as shell and returns the output.
    # If the command doesn't return a successful status code, this function throws.
    @staticmethod
    def RunShellCommand(cmd:str) -> str:
        # Check=true means if the process returns non-zero, an exception is thrown.
        # Shell=True is required so non absolute commands like "systemctl restart ..." work
        result = subprocess.run(cmd, check=True, shell=True, capture_output=True, text=True)
        return result.stdout


    # Ensures a folder exists, and optionally, it has permissions set correctly.
    @staticmethod
    def EnsureDirExists(dirPath, context:Context, setPermissionsToUser = False):
        # Ensure it exists.
        Logger.Header("Enuring path and permissions ["+dirPath+"]...")
        if os.path.exists(dirPath) is False:
            Logger.Info("Dir doesn't exist, creating...")
            os.mkdir(dirPath)
        else:
            Logger.Info("Dir already exists.")

        if setPermissionsToUser:
            Logger.Info("Setting owner permissions to the service user ["+context.UserName+"]...")
            uid = pwd.getpwnam(context.UserName).pw_uid
            gid = pwd.getpwnam(context.UserName).pw_gid
            # pylint: disable=no-member # Linux only
            os.chown(dirPath, uid, gid)

        Logger.Info("Directory setup successfully.")


    # Helper to ask the user a question.
    @staticmethod
    def AskYesOrNoQuestion(question:str) -> bool:
        val = None
        while True:
            try:
                val = input(question+" [y/n] ")
                val = val.lower().strip()
                if val == "n" or val == "y":
                    break
            except Exception as e:
                Logger.Warn("Invalid input, try again. Logger.Error: "+str(e))
        return val == "y"


    @staticmethod
    def PrintServiceLogsToConsole(context:Context):
        if context.ServiceName is None:
            Logger.Warn("Can't print service logs, there's no service name.")
            return
        try:
            result = Util.RunShellCommand("sudo journalctl -u "+context.ServiceName+" -n 20 --no-pager")
            # Use the logger to print the logs, so they are captured in the log file as well.
            Logger.Info(result)
        except Exception as e:
            Logger.Error("Failed to print service logs. "+str(e))
