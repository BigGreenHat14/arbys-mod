import time as timelib
from random import randint
from clockdisplay import OverlayEngine
import playsound3
import keyboard

import random
KEYS = "AbcdEfGHJLNPrtUy3467"
def my_background_logic(ui: OverlayEngine):
    time = randint(ui.params["timerrange"][0]*60,ui.params["timerrange"][1]*60)
    key = ""
    if ui.params["onlyquick"]:
        if ui.params["hmchance"] == 0:
            print("WARNING: QuickTime is set to Off, nothing will happen")
        ui.update_text("rEAdy")
        while True:
            timelib.sleep(1.2)
            playsound3.playsound(("tick.wav" if not ui.params["irl"] else "irl_tick.wav") if not ui.params["moan"] else "moan.wav", block=False)
            if random.randint(1,ui.params["hmchance"]) == 1:
                key = random.choice(KEYS)
                ui.update_text(f"tYpE {key}")
                start = timelib.time()
                while timelib.time() - start < 2 * ui.params["timermult"]:
                    if keyboard.is_pressed(key.lower()):break
                if timelib.time() - start >= 2 * ui.params["timermult"]:
                    break  
                ui.update_text("rEAdy")
    else:
        for i in range(time,0,-1):
            if ui.params["hmchance"] != 0 and random.randint(1,ui.params["hmchance"]) == 1:
                key = random.choice(KEYS)
                ui.update_text(f"tYpE {key}")
                start = timelib.time()
                while timelib.time() - start < 2 * ui.params["timermult"]:
                    if keyboard.is_pressed(key.lower()):break
                if timelib.time() - start >= 2 * ui.params["timermult"]:
                    break
            else:
                ui.update_text(f"{i // 60}:{str(i % 60).zfill(2)}")
                if ui.params["sounds"]:
                    playsound3.playsound(("tick.wav" if not ui.params["irl"] else "irl_tick.wav") if not ui.params["moan"] else "moan.wav", block=False)
                    timelib.sleep(1.2 * ui.params["timermult"])
                else:
                    timelib.sleep(1 * ui.params["timermult"])    
    print("Closing overlay window...")
    ui.close() # <--- This will trigger the window to close and exit the app cleanly

def wait(sounds,fill,timerrange,color,timermult,hmchance,real,moan,onlyquick):
    if real:
        ui = OverlayEngine(
            image_path="timer_real.png",
            font_file_path="7segment.ttf",
            initial_text="-:--",
            text_x=40,
            text_y=160,
            font_size=80,
            font_color=color,
            fullscreen=fill,
            aspect_ratio_mode=OverlayEngine.STRETCH_TO_FILL,
            params={"timermult":timermult,"timerrange":timerrange,"sounds":sounds,"hmchance":hmchance,"moan":moan,"irl":real,"onlyquick":onlyquick}
        )
    else:
        ui = OverlayEngine(
            image_path="timer.png",
            font_file_path="7segment.ttf",
            initial_text="-:--",
            text_x=256,
            text_y=160,
            font_size=80,
            font_color=color,
            fullscreen=fill,
            aspect_ratio_mode=OverlayEngine.STRETCH_TO_FILL,
            params={"timermult":timermult,"timerrange":timerrange,"sounds":sounds,"hmchance":hmchance,"moan":moan,"irl":real,"onlyquick":onlyquick}
        )
    ui.launch(my_background_logic)