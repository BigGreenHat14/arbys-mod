# Arbys mod

you get arbys ads on a timer*

*for the most part

## Setup
1. CD into the extracted zip

1. Get Python

1. Run `python -m pip install -r requirements.txt`

1. Run `python main.py`

## Config
```

Low, Normal or High (defaults to Normal)
TimerLength - Timer Length (L=1-2, N=3-5, H=5-8)
TimerSpeed - Timer Speed Multiplier (L=2, N=1, H=0.5)

Low, Normal, High or Off (defaults to Off)
QuickTime - Makes you type a letter randomly, has a chance every tick (L=1/30, N=1/20, H=1/10)
AshChance - Makes the Ashley Graves video appear randomly (L=1%, N=5%, H=25%)

Yes or No
ResetConfig - Resets Config
OnlyQuickTime - Disables the timer
AlwaysAsh - Always shows the Ashley Graves video
AshWarning - Makes the timer pink if the Ashley Graves video is chosen.
HideTimer - Hides the timer (also disables timer ticks and quicktime)
GamingSafety - Presses escape when a video is about to play
TimerTicks - Plays ticking sounds for each timer tick
FreakyTick - Plays moaning sounds for each timer tick (requires TimerTicks)
EmergencyExit - Allows you to escape the video (doesn't block keys)
DisownProtection - Mutes the Ashley Graves video
FakeWarn - Shows pink or green on the timer (regardless of video or AshWarning)
HideMessage - Hides "ts gonna be ____" logs
Gas - Plays a burp sound before a video plays
IRL - Replaces normal ticking sounds and the clock with real life versions
Balls - Very cool
Yes - Of course, yes
No - Nope, nada, no way
Torture - *REDACTED*


Any color except green (Red, Orange, Yellow, Blue, Purple or White, defaults to Red)
TimerColor - Self Explanatory
```

## Technichal

This uses VLC media player internally, to allow for easy video playing.

TODO: add this
