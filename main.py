import os
import sys
import configparser
os.chdir(os.path.dirname(__file__))

# Initialize the parser
ini = configparser.ConfigParser()
ini.read("config.ini")
config = dict(ini["DEFAULT"])
print(config)
if config["resetconfig"] == "Yes":
    DEFAULT_CONFIG = """[DEFAULT]
; Set this to Yes if you want to reset your config (Yes or No)
ResetConfig=No

; Low, Normal or High (defaults to Normal)
TimerLength=Normal
TimerSpeed=Normal

; Low, Normal, High or Off (defaults to Off)
QuickTime=Off
AshChance=Normal

; Yes or No
OnlyQuickTime=No
AlwaysAsh=No
AshWarning=No
HideTimer=No
GamingSafety=No
TimerTicks=No
FreakyTick=No
EmergencyExit=No
DisownProtection=No
FakeWarn=No
HideMessage=No
Gas=No
IRL=No

; Any color except green (Red, Orange, Yellow, Blue, Purple or White, defaults to Red)
TimerColor=Red

; Experimental?? (Yes or No)
Balls=Yes
Yes=Yes
No=No
Torture=No"""
    with open("config.ini","w") as f:
        f.write(DEFAULT_CONFIG)
    print("Config Reset!")
    sys.exit(0)

timer_range = {"Low":(1,2),"Normal":(3,5),"High":(5,8)}.get(config["timerlength"],(3,5))
ash_chance = {"Low":1,"Normal":5,"High":25,"Off":0}.get(config["ashchance"],0)
fast_timer = {"Low":2,"Normal":1,"High":0.5}.get(config["timerspeed"],1)
hardmode = {"Low":30,"Normal":20,"High":10,"Off":0}.get(config["quicktime"],0)
if config["alwaysash"] == "Yes":
    ash_chance = 100

ash_warn = config["ashwarning"] == "Yes" #
no_timer = config["hidetimer"] == "Yes" #
auto_esc = config["gamingsafety"] == "Yes" #
timer_screen = config["no"] == "Yes" #
timer_ticks = config["timerticks"] == "Yes" #
triple_play = config["torture"] == "Yes" #
emergency_exit = config["emergencyexit"] == "Yes"
disown_protection = config["disownprotection"] == "Yes"
always_fart = config["yes"] != "Yes"
fakeout = config["fakewarn"] == "Yes"
message = config["hidemessage"] != "Yes"
moan = config["freakytick"] == "Yes"
burp = config["gas"] == "Yes"
onlyquick = config["onlyquicktime"] == "Yes"
balls = config["balls"] != "Yes"
irl = config["irl"] == "Yes"
timercolor = {"Red":"#FF0000","Orange":"#FFAE00","Yellow":"#FFFF00","Blue":"#0000FF","Purple":"#9900FF","White":"#FFFFFF"}.get(config["timercolor"],"#FF0000")

# 1. TELL WINDOWS EXACTLY WHERE THE SYSTEM VLC LIVE APPLICATION IS
# This forcefully bypasses the "libvlc.dll not found" error on Windows.
DIR = os.path.dirname(__file__)

if sys.platform == 'win32':
    if os.path.exists(DIR):
        os.add_dll_directory(DIR)
    else:
        print(f"Error: Could not find VLC installed at '{DIR}'.")
        print("Please ensure you have installed the 64-bit version of VLC Media Player.")
        exit(1)

# Now it is safe to import python-vlc bindings
import vlc
import time
import random
import clock
import keyboard

# CONFIGURATION
# Replace this with the full path to your video file
VIDEO_PATH = os.path.join(DIR,"arbys.mp4")
VIDEO_PATH_ASH = os.path.join(DIR,"ash_new.mp4")
VIDEO_PATH_FART = os.path.join(DIR,"fart.mp4")
if emergency_exit:
    BLOCK_LIST = []
else:
    BLOCK_LIST = ["win","tab","esc","f4"]

if not os.path.exists(VIDEO_PATH):
    print(f"Error: Could not find video file at '{VIDEO_PATH}'.")
    exit(1)

def main():
    print("Initializing main VLC media engines...")
    # We initialize the default global player app instance
    instance = vlc.Instance(
        '--no-video-title-show', 
        '--input-fast-seek',
        '--file-caching=100',
        '--quiet',
        '--video-on-top'
    )
    player_normal = instance.media_player_new()
    player_ash = instance.media_player_new()
    player_fart = instance.media_player_new()
    # Pack media definitions
    media_normal = instance.media_new(VIDEO_PATH)
    media_ash = instance.media_new(VIDEO_PATH_ASH)
    media_fart = instance.media_new(VIDEO_PATH_FART)
    player_normal.set_media(media_normal)
    player_ash.set_media(media_ash)
    player_fart.set_media(media_fart)
    
    # Absolute lockdown parameters
    player_ash.set_fullscreen(True)
    player_ash.video_set_key_input(False)
    player_ash.video_set_mouse_input(False)

    player_normal.set_fullscreen(True)
    player_normal.video_set_key_input(False)
    player_normal.video_set_mouse_input(False)

    player_fart.set_fullscreen(True)
    player_fart.video_set_key_input(False)
    player_fart.video_set_mouse_input(False)

    print("Engines ready. Starting scheduled loop sequence.")

    try:
        while True:
            timer_color = timercolor
            ash = False
            if (always_fart or (random.randint(1,1000) == 1)) and not balls:
                player = player_fart
                if ash_warn:
                    timer_color = "#00FF88"
                if message:print("ts gonna be fragrent")
            elif (random.randint(1,100) <= ash_chance) and not balls:
                ash = True
                player = player_ash
                if ash_warn:
                    timer_color = "#FF88CD"
                if message:print("ts gonna be freaky")
            else:
                player = player_normal
                if message:print("ts gonna be foody")
            if fakeout:
                choice = random.randint(1,6)
                if choice == 1:
                    timer_color = "#00FF88"
                elif choice == 2:
                    timer_color = "#FF88CD"
                elif choice == 3:
                    timer_color = timercolor

            if not no_timer:
                clock.wait(timer_ticks,timer_screen,timer_range,timer_color,fast_timer,hardmode,irl,moan,onlyquick)
            else:
                time.sleep(random.randint(*timer_range) * fast_timer)
            print("Playing video fullscreen...")
            if auto_esc: keyboard.press_and_release("esc")
            for i in BLOCK_LIST:keyboard.block_key(i)
            if burp:clock.playsound3.playsound("burp.wav")
            player.play()
            
            # Brief wait for engine state transition processing
            time.sleep(0.2)
            player.audio_set_mute(disown_protection and ash)
            # Let it run completely uninterrupted until the file stream terminates
            while player.get_state() not in [vlc.State.Ended, vlc.State.Error, vlc.State.Stopped]:
                time.sleep(0.2)
                
            print("Video finished playing.")
            player.stop()
            if triple_play:
                time.sleep(0.2)
                player.play()
                time.sleep(0.2)
                player.audio_set_mute(disown_protection and ash)
                while player.get_state() not in [vlc.State.Ended, vlc.State.Error, vlc.State.Stopped]:
                    time.sleep(0.2)
                player.stop()
                time.sleep(0.2)
                player.play()
                time.sleep(0.2)
                player.audio_set_mute(disown_protection and ash)
                while player.get_state() not in [vlc.State.Ended, vlc.State.Error, vlc.State.Stopped]:
                    time.sleep(0.2)
                player.stop()

            # Set a random sleep delay interval between 3 and 5 minutes
            next_interval = random.randint(180, 300)
            minutes, seconds = next_interval // 60, next_interval % 60
            print(f"Waiting {minutes}m {seconds}s until next loop playback triggers...")
            for i in BLOCK_LIST:
                try:
                    keyboard.unblock_key(i)
                except KeyError:
                    pass
            

    except KeyboardInterrupt:
        print("\nShutting down loop script configuration.")
    finally:
        # Resource cleanup
        player.release()
        instance.release()

if __name__ == "__main__":
    main()