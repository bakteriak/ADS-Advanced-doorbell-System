## Advanced doorbell system
import os
from picamera import PiCamera
from gpiozero import MotionSensor, Button, Buzzer
from time import sleep
from sense_hat import SenseHat
from twython import Twython
from auth import (
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
    )

camera = PiCamera()
sense = SenseHat()
sensor = MotionSensor(14)
button = Button(18)
buzz = Buzzer(24)
twitter = Twython(
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
    )

def sensors():
    temp = round(sense.get_temperature())
    hum = round(sense.get_humidity())

    r = (225, 0, 0)
    w = (0, 0, 255)

    smile = [
        w, w, w, w, w, w, w, w,
        w, w, w, w, w, w, w, w,
        w, w, r, w, w, r, w, w,
        w, w, w, w, w, w, w, w,
        w, r, w, w, w, w, r, w,
        w, w, r, r, r, r, w, w,
        w, w, w, w, w, w, w, w,
        w, w, w, w, w, w, w, w, 
    ]

    sad = [
        w, w, w, w, w, w, w, w,
        w, w, w, w, w, w, w, w,
        w, w, r, w, w, r, w, w,
        w, w, w, w, w, w, w, w,
        w, w, w, w, w, w, w, w,
        w, w, r, r, r, r, w, w,
        w, r, w, w, w, w, r, w,
        w, w, w, w, w, w, w, w, 
    ]


    sense.set_pixels(sad)
    sleep(2)
    sense.clear(r)
    sense.clear()

    sense.set_pixels(smile)
    sleep(2)
    red = (255, 0, 0)
    blue = (0, 0, 255)

    sense.clear(r)
    sense.clear()

    #sense.set_pixel(red)

    sense.show_message("ADS",back_colour=blue, text_colour = red)

    sense.clear(red)
    sense.clear()

    data = sense.get_orientation()
    pitch = data['pitch']

    print(pitch)

    print(temp)
    Tempstr=str(temp)
    Humstr =str(hum)
    sense.show_message("Temp"+Tempstr+" C",back_colour=blue, text_colour = red)
    print(hum)
    sense.show_message("Hum:"+Humstr,back_colour=blue, text_colour = red)
    if hum > 29:
        sense.clear(255, 0,0)
        sense.clear(red)
        sense.clear(blue)
        sense.clear()
    else:
        sense.clear(0, 0, 255)
        sense.clear(red)
        sense.clear(blue)
        sense.clear()
        sleep(0.1)

def motion():
    print('motion')
    if sensor.motion_detected:
        print("motion detected we have you on camera :)")    
        camera.start_preview(alpha=192)
        sleep(2)
        camera.capture("/home/pi/image.jpg")
        camera.stop_preview()

        photo = open('/home/pi/image.jpg', 'rb')
        response = twitter.upload_media(media=photo)
        twitter.update_status(status='Answer the door! @bakteriak @richywatt247 @gbuick423 #Picademy', media_ids=[response['media_id']])

def pressed():
    print('pressed')
    if button.is_pressed:
        buzz.on()
        sleep(1)
        buzz.off()
        buzz.on()
        sleep(1)
        buzz.off()
        print("Recording started....")
        camera.start_preview(alpha=192)
        camera.framerate = 24
        camera.start_recording("/home/pi/ADS.h264")
        camera.wait_recording(10)
        camera.stop_preview()

        print("Converting vdeo to mp4")
        os.system("avconv -r 24 -i '/home/pi/ADS.h264' -vcodec copy '/home/pi/ADS.mp4'")
        print("Sending video.....")
        
        video = open('/home/pi/ADS.mp4', 'rb')
        response = twitter.upload_video(media=video, media_type='video/mp4')
        twitter.update_status(status='Got your video! @bakteriak @richywatt247 @gbuick423 #Picademy', media_ids=[response['media_id']])

while True:
    sensor.wait_for_motion()
    motion()
    button.wait_for_press()
    pressed()
    sensors()
    sleep(10)
