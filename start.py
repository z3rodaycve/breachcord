import os

# Console Colors
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ================================================
#                   Installation
# ================================================

# Installation Variables
pip_version = 0

# Install Methods 
def automatic_install():
    print(f"{bcolors.OKCYAN}[CHECKING]{bcolors.ENDC} Checking for {bcolors.OKBLUE}pip{bcolors.ENDC}")

    pip = os.popen("pip --version")
    pip = pip.read()
    if pip == "":
        print(f"{bcolors.FAIL}[ERROR]{bcolors.ENDC} Python PIP was not found. Trying again.")
        
        pip2 = os.popen("python -m pip")
        pip2 = pip2.read()
        if pip2 == "":
            print(f"{bcolors.FAIL}[FAIL]{bcolors.ENDC} Failed to find PIP. Do you have it installed? Try again or run manual installation.")
            raise SystemExit
        else:
            pip_version = 2
            print(f"{bcolors.OKGREEN}[SUCCESSFUL]{bcolors.ENDC} Python PIP was found. Installing dependencies now. | Info:{bcolors.BOLD}", pip.strip(), bcolors.ENDC)
    else:
        pip_version = 1
        print(f"{bcolors.OKGREEN}[SUCCESSFUL]{bcolors.ENDC} Python PIP was found. Installing dependencies now. | Info:{bcolors.BOLD}", pip.strip(), bcolors.ENDC)

    print(f"{bcolors.OKCYAN}[DEPENDENCIES INSTALL]{bcolors.ENDC} Installing all required dependencies from {bcolors.BOLD}requirements.txt{bcolors.ENDC}")
    if pip_version == 1:
        dep_install = os.popen("pip install -r requirements.txt")
    if pip_version == 2:
        dep_install = os.popen("python -m pip install -r requirements.txt")

    print(f"{bcolors.OKGREEN}[DEPENDENCIES INSTALLED]{bcolors.ENDC} Sucessfully installed all of the required dependencies from {bcolors.BOLD}requirements.txt{bcolors.ENDC}")
    print(f"{bcolors.OKCYAN}[INFO]{bcolors.ENDC} Rerun this Python file again to start the Discord Bot | {bcolors.BOLD}press any key to continue{bcolors.ENDC}")
    input()

def manual_install():
    print(f"{bcolors.WARNING}[NOTICE]{bcolors.ENDC} If you have never installed Python libraries, please run {bcolors.BOLD}AUTOMATIC{bcolors.ENDC} install instead.")
    print(f"{bcolors.OKCYAN}[INSTALLATION INFO]{bcolors.ENDC} Please install all required Python libraries, then {bcolors.BOLD}press any key{bcolors.ENDC} here to finish the installation process.")
    input()

def lock_install(install_lock):
    with open(install_lock, "w") as f:
            f.write("This file was automatically generated because of finished installation process made by Breachcord. To restart installation process, please delete this file.")

# ================================================
#                Installation Check
# ================================================

current_dir = os.path.dirname(os.path.abspath(__file__))
install_lock = os.path.join(current_dir, ".install-lock")

if os.path.isfile(install_lock):
    print(f"{bcolors.OKCYAN}[INFO]{bcolors.ENDC} Breachcord has detected an installation. If you think that this is a mistake or you would like to re-run the installation process, please delete the {bcolors.BOLD}.install-lock{bcolors.ENDC} file.")
    os.system('python bot.py')
else:
    install_preference = input(f"Do you want to run {bcolors.BOLD}AUTOMATED{bcolors.ENDC}(1) or {bcolors.BOLD}MANUAL{bcolors.ENDC}(2) installation?        ")
    
    if install_preference != "1" and install_preference != "2":
        print(f"{bcolors.FAIL}[INPUT ERROR]{bcolors.ENDC} Invalid input '", install_preference, f"'. Please answer with {bcolors.BOLD}1{bcolors.ENDC} or {bcolors.BOLD}2{bcolors.ENDC}")
        raise SystemExit

    if install_preference == "1":
        automatic_install()
        lock_install(install_lock)
    else:
        manual_install()
        lock_install(install_lock)
