import cv2
from pyzbar.pyzbar import decode
import os

if os.name == 'nt':  # Only on Windows
    import winsound

# import winsound

# Beep sound parameters
def play_beep():
    frequency = 1000  # Set Frequency To 1000 Hertz
    duration = 500  # Set Duration To 500 ms (0.5 seconds)
    winsound.Beep(frequency, duration)

# Capture webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")


while cap.isOpened():
    success, frame = cap.read()
    # Flip the image like mirror image
    frame = cv2.flip(frame, 1)
    # Detect the barcode
    detectedBarcode = decode(frame)

    for barcode in detectedBarcode:
        # Decode the barcode data
        barcode_data = barcode.data.decode('utf-8')
        if barcode_data:
            print(f"{barcode_data}")
            cv2.putText(frame, barcode_data, (50, 50), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 255), 2)
            play_beep()
            cv2.imwrite("code.png", frame)

            # Exit the program after detecting a barcode
            cap.release()
            cv2.destroyAllWindows()
            exit()

    cv2.imshow('scanner', frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
