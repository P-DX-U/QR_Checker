import subprocess
import qrcode

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

def create_qr_code(data, filename):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)

    print("QR code generated successfully > \n" + 
          "Data: " + data + "\n" + 
          "Saved as: " + filename + "\n")
    
