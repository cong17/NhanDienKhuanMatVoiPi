from threading import Thread
import os


# Ham phat ra am thanh
def play_sound(path):
    os.system("mpg123 "+path)

t = Thread(target=play_sound, args=("sounds/ready.mp3", ))
t.deamon = True
t.start()