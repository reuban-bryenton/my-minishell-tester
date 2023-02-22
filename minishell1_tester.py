import json
import subprocess
import sys
import colorama
from colorama import Fore

def reset_color():
    print(Fore.RESET)

def print_diff(mot, tmot):
    print(Fore.YELLOW, "---MYSH---")
    print(mot)
    print(Fore.YELLOW, "---TCSH---")
    print(tmot)
    print(Fore.YELLOW, "---END---")
    reset_color()

def exec_process_echo(test, md):
    try:
        echocmds = test['commands']
        bf = ""
        bf += "echo -e '{0}'\n".format('echo "' + echocmds[0] + '" | ' + sys.argv[1])
        if test['sleeptime'] > 0:
            bf += "sleep {0}\n".format(test['sleeptime'])
        tst_file = open("tmp", "w")
        tst_file.write(bf)
        tst_file.close()
        #eproc = subprocess.Popen(("/bin/bash", "-C", "tmp"), stdout=subprocess.PIPE)
        #exc = ["echo", echocmds[0]]
        #proc = subprocess.Popen((exc), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
        #proc.communicate(echocmds[0]) if not md else proc.communicate("tcsh")
        #proc.wait(10)
        #ot = proc.stdout.read()
        cmd = sys.argv[1] if not md else "tcsh"
        ot = subprocess.check_output("echo \"{0}\" | {1}".format(echocmds[0], cmd), shell=True)
        ot = ot.decode()
        return 0, ot #proc.returncode, ot
    except subprocess.TimeoutExpired:
        return 139, None
    except Exception as e:
        return -1, None

def exec_process(test, md):
    try:
        if (test['echo'] == 1):
            return exec_process_echo(test, md)
        cmds = test['commands']
        bf = ""
        for cmd in cmds:
            bf += "echo -e '{0}'\n".format(cmd)
            if test['sleeptime'] > 0:
                bf += "sleep {0}\n".format(test['sleeptime'])
        if (len(cmds) == 0):
            if test['sleeptime'] > 0:
                bf += "sleep {0}\n".format(test['sleeptime'])
        tst_file = open("tmp", "w")
        tst_file.write(bf)
        tst_file.close()
        eproc = subprocess.Popen(("/bin/bash", "-C", "tmp"), stdout=subprocess.PIPE)
        exc = sys.argv[1] if not md else "tcsh"
        proc = subprocess.Popen((exc), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=eproc.stdout)
        proc.wait(10)
        ot = proc.stdout.read()
        return proc.returncode, ot
    except subprocess.TimeoutExpired:
        return 139, None
    except Exception as e:
        return -1, None

def start_test(test):
    mrcode, mot = exec_process(test, False)
    expcode, tmot = exec_process(test, True)
    if (test['echo']):
        print(Fore.YELLOW, "🗒️ Note: echo commands are in beta.".format(test['name']))
    expcode = test['override_excode']
    if expcode >= 0 and mrcode != expcode and expcode != 139:
        print(Fore.RED, "❌ Test [{0}]: Test failed.".format(test['name']))
        print(Fore.BLUE, "ℹ️  expexted: {0} but got: {1}".format(expcode, mrcode))
        reset_color()
        return False
    elif expcode < 0 and (mrcode == 139 or mrcode == 11):
        print(Fore.MAGENTA, "❌ Test [{0}]: Test crashed.".format(test['name']))
        reset_color()
        return False
    if mrcode == -1:
        print(Fore.RED, "❌ Test [{0}]: Test failed. Unable to start.".format(test['name']))
        reset_color()
        return False
    if mot != tmot:
        print(Fore.RED, "❌ Test [{0}]: Test failed. Difference.".format(test['name']))
        print_diff(mot, tmot)
        return False
    print(Fore.GREEN, "✅ Test [{0}]: Test passed.".format(test['name']))
    reset_color()
    return True

def main():
    tests = None
    npassed = 0
    nfailed = 0
    ntests = 0

    if len(sys.argv) != 2:
        print(Fore.RED + "❌ Wrong args (use -h for help)")
        return 1

    if (sys.argv[1] == "-h"):
        print(Fore.YELLOW + "\n👋 Welcome to minishell1 tester by @reuban_bryenton\n")
        print(Fore.YELLOW + "To use this tool type in the following command:")
        print(Fore.YELLOW + "\t'python3 minishell1_tester.py ./{binary name}'\n")
        return 0

    try:
        fl = open("tests.json")
        cnt = fl.read()
        tests = json.loads(cnt)
    except IOError as e:
        print(Fore.RED + "❌ Unable to open tests.json: no such file or permission denied.")
        return 1

    if tests is None:
        print(Fore.RED + "❌ Unable to load tests from tests.json.")
        return 1

    
    for q in tests:
        ntests += 1
    print(Fore.CYAN + "\nTesting [{0}] tests...\n".format(ntests))

    for q in tests:
        if start_test(q):
            npassed += 1
        else:
            nfailed += 1

    print(Fore.GREEN, "✅ Passed: {0}".format(npassed))
    print(Fore.RED, "❌ Failed: {0}\n".format(nfailed))
    reset_color()
    return 0

if __name__ == "__main__":
    exit(main())

