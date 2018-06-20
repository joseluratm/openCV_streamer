#!/usr/bin/env python
from flask import Flask, render_template, Response
import cv2
from skimage.measure import compare_ssim
import argparse
import imutils
import telegram
import time


app = Flask(__name__)
vc = cv2.VideoCapture(0)
bot = telegram.Bot(token='TOKEN')

@app.route('/viewHome')
def index():    
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(generateFrame(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def generateFrame():
    
    while True:
        lastTime = time.time()
        frameOld = cv2.imread("frame.png")
        rval, frame = vc.read()
        both_img = cv2.flip(frame, 1)
        small = cv2.resize(both_img, (0,0), fx=0.5, fy=0.5)

        #checkeamos que el anterior frame y el nuevo no son iguales
        grayA = cv2.cvtColor(frameOld, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        (score, diff) = compare_ssim(grayA, grayB, full=True)
        diff = (diff * 255).astype("uint8")
        #Si el porcentaje de diferencia es mayor del 0.9 es que esta todo guay. Si no algo raro ahii
        if score > 0.9:
            cv2.putText(small,"No hay nada nuevo...", (0,20), cv2.FONT_HERSHEY_SIMPLEX, 1, 255)
        else:
            actualTime = time.time()
            cv2.putText(small,"Algo raro hay!!", (0,20), cv2.FONT_HERSHEY_SIMPLEX, 1, 255)
            if (actualTime - lastTime)> 5:                
                bot.send_message(chat_id='ID_CHAT',text='Alguien te hackeo la casa :O')
                bot.send_photo(chat_id='ID_CHAT', photo=open('frame.png', 'rb'))
                lastTime = time.time()
        cv2.imwrite('frame.png', small)
        
        yield (b'--frame\r\n'
               b'Content-Type: image/png\r\n\r\n'
                + open('frame.png', 'rb').read() + b'\r\n')



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
