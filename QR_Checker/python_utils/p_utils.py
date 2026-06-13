import subprocess

def make_hash(register_string):
    # Running of $echo -n "register_string" | sha256sum | awk '{ print $1 }' 
    # in secuential order and capture output.

    echo = subprocess.Popen(['echo', '-n', register_string], stdout=subprocess.PIPE)
    sha256 = subprocess.Popen(['sha256sum'], stdin=echo.stdout, stdout=subprocess.PIPE)
    awk = subprocess.check_output(['awk', '{ print $1 }'], stdin=sha256.stdout, text=True)

    result = awk

    print("Hash generated successfully > \n" + 
          "Original String: " + register_string + "\n" + 
          "Hash Generated: " + result + "\n")

    return result
