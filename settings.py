import pygame
import pygame.freetype
import atexit
import saved
import os

# ─── Pi Zero 2W / 480×320 HyperPixel optimizations ───────────────────────────
# Tell SDL2 to use its own ARM-optimised blitter instead of pygame's default.
# Must be set BEFORE pygame.init() is called (done here at import time).
os.environ.setdefault('PYGAME_BLEND_ALPHA_SDL2', '1')
# Uncomment the line below to run directly on the framebuffer (no X11 needed):
# os.environ.setdefault('SDL_VIDEODRIVER', 'kmsdrm')
# os.environ.setdefault('SDL_AUDIODRIVER', 'alsa')
# ─────────────────────────────────────────────────────────────────────────────

# Custom
name = "ZapWizard"

# SCREEN  ── native 480×320 to avoid any software scaling overhead
WIDTH = 480
HEIGHT = 320
FULLSCREEN = True   # forces FULLSCREEN on Pi (avoids window manager overhead)

# Menu Position  (scaled from original 720×720)
menu_x = 7
menu_y = 62

# Footer Position
footer_x = 0
footer_y = 280

# Description box Position
description_box_x = 233
description_box_y = 107

# COLORS
black = (0, 0, 0)
bright = (0, 230, 0)
light = (0, 170, 0)
mid = (0, 120, 0)
dim = (0, 70, 0)
dark = (0, 40, 0)

# MAP
# MAP_FOCUS = (-5.9347681, 54.5889076)
# MAP_FOCUS = (-102.3016145, 21.8841274) #Old Default?
# MAP_FOCUS = (-118.5723894,34.3917171)#CodeNinjasValencia
# MAP_FOCUS = (32.7157, 117.1611)
# MAP_FOCUS = (-92.1943197, 38.5653437)
# MAP_FOCUS = (-98.0878917, 30.1914818) # Zap's Hometown
MAP_FOCUS = (-116.2158, 33.7206)  # Indio, CA
# Cached map avoids OSM network fetch and tile re-render on every boot.
# Set to False only when you need to regenerate the map cache.
LOAD_CACHED_MAP = True

# Open Street Map settings
WORLD_MAP_FOCUS = 0.07  # Needed to handle the 50k node limit from OSM

# Google maps:
MAP_TYPE = "hybrid"  # Select Hybrid if you want labels and roads, satellite if you want imagry only
MAP_STYLE = "feature:all|geometry.stroke|labels.text.stroke"
WORLD_MAP_ZOOM = 12
LOCAL_MAP_ZOOM = 17

EVENTS = {
    'SONG_END': pygame.USEREVENT + 1,
    'PLAYPAUSE': pygame.USEREVENT + 2,
    'HOLOTAPE_END': pygame.USEREVENT + 3
}

MODULES = {
    0: "STAT",
    1: "INV",
    2: "DATA",
    3: "MAP",
    4: "RADIO",
    5: "BOOT",
    6: "PASSCODE"
}

MODULE_TEXT = ["STAT", "INV", "DATA", "MAP", "RADIO"]

STARTER_MODULE = "data"

ACTIONS = {
    pygame.K_F1: "module_stats",
    pygame.K_F2: "module_items",
    pygame.K_F3: "module_data",
    pygame.K_F4: "module_map",
    pygame.K_F5: "module_radio",
    pygame.K_F6: "module_boot",
    pygame.K_F7: "module_passcode",
    pygame.K_1: "knob_1",
    pygame.K_2: "knob_2",
    pygame.K_3: "knob_3",
    pygame.K_4: "knob_4",
    pygame.K_5: "knob_5",
    pygame.K_UP: "dial_up",
    pygame.K_DOWN: "dial_down",
    pygame.K_PLUS: "zoom_in",
    pygame.K_EQUALS: "zoom_in",
    pygame.K_MINUS: "zoom_out",
    pygame.K_KP_PLUS: "zoom_in",
    pygame.K_KP_MINUS: "zoom_out",
}

# Using GPIO.BCM as mode
GPIO_ACTIONS = {
    #    19: "module_stats", #GPIO 4
    #    26: "module_items", #GPIO 14
    #    16: "module_data", #GPIO 15
    #	18:	"knob_1", #GPIO 18 Do Not enable messes with the screen.
    #	18: "knob_2", #GPIO 18 Turns screen off do not use
    #	7: "knob_3", #GPIO 7
    #	22: "knob_1", #GPIO 22
    #	22: "dial_down", #GPIO 22
    #	25: "dial_up", #GPIO 25
    #    20: "knob_2", #GPIO 24
    #	25: "knob_3" #GPIO 23
}

FOOTER_RADIO = ["", "", "", "", False]

SPECIAL = [
    ["Strength", 4, "images/stats/special/strength",
     "Strength is a measure of your raw physical power. It affects how much you can carry, and the damage of all melee attacks."],
    ["Perception", 8, "images/stats/special/perception",
     "Perception is your environmental awareness and 'sixth sense', and affects weapon accuracy in V.A.T.S."],
    ["Endurance", 3, "images/stats/special/endurance",
     "Endurance is a measure of your overall physical fitness. It affect your total Health and the Action Point drain from sprinting."],
    ["Charisma", 5, "images/stats/special/charisma",
     "Charisma is your ability to charm and convince others. It affects your success to persuade in dialogue and prices when you barter."],
    ["Intelligence", 6, "images/stats/special/intelligence",
     'Intelligence is a measure of your overall metal acuity, and affects the number of Experience Points earned'],
    ["Agility", 3, "images/stats/special/agility",
     "Agility is a measure of your overall fitnesse and reflexes. It affects the number of Action Points in V.A.T.S. and your ability to sneak"],
    ["Luck", 3, "images/stats/special/luck",
     "Luck is a measure of your general good fortune, and affects the recharge rate of Critical Hits"],
]

STATUS_FOOTER = ["HP 90/100", "LEVEL 120", "AP 90/90", 90, True]

WEAPONS = [
    ["10mm Pistol", "1", "images/inventory/10mmpistol", "",
     [["Damage", 18], ["10mm", 57, ], ["Fire Rate", 46], ["Range", 83], ["Accuracy", 60], ["Weight", 3.5],
      ["Value", 50]]],
    ["Bottle Cap Mine", "1", "images/inventory/bottlecapmine", "",
     [["Damage", 301], ["Fire Rate", 0], ["Range", 93], ["Accuracy", 0], ["Weight", 0.5], ["Value", 75]]],
    ["Combat Knife", "1", "images/inventory/combatknife", "",
     [["Damage", 10], ["Speed", "FAST"], ["Weight", 1], ["Value", 25]]],
    ["Fragmentation Grenade", 2, "images/inventory/grenadefrag", "",
     [["Damage", 151], ["Fire Rate", 0], ["Range", 93], ["Accuracy", 0], ["Weight", 0.5], ["Value", 50]]],
    ["Laser Musket", 1, "images/inventory/lasermusket", "",
     [["Damage", 30], ["Cell", 30], ["Fire Rate", 6], ["Range", 107], ["Accuracy", 70], ["Weight", 12.6],
      ["Value", 61]]],
    ["Laser Rifle", 1, "images/inventory/laserrifle", "",
     [["Damage", 30], ["Cell", 30], ["Fire Rate", 6], ["Range", 107], ["Accuracy", 70], ["Weight", 12.6],
      ["Value", 61]]],
    ["Plasma Mine", 3, "images/inventory/plasmamine", "",
     [["Damage", 150], ["Fire Rate", 0], ["Range", 93], ["Accuracy", 0], ["Weight", 0.5], ["Value", 100]]],
]

FOOTER_WEAPONS = ["WEIGHT 186/200", "CAPS: 35", "AMMO: 500", None, False]

ARMOR = [
    ["Vault 111 Jumpsuit", "", "images/inventory/armor_suit", "", [["DMG Resist", 5], ["Weight", 1], ["Value", 20]]],
    ["Mask", "", "images/inventory/armor_mask", "", [["INT", 8], ["Weight", 0.2], ["Value", 30]]],
    ["Eyeglasses", "", "images/inventory/armor_glasses", "", [["PER", 1], ["Weight", 0.1], ["Value", 7]]],
    ["Helmet", "", "images/inventory/armor_helmet", "", [["PER", -1], ["Weight", 1], ["Value", 10]]],
    ["Chest Armor", "", "images/inventory/armor_chest", "", [["PER", 1], ["Weight", 3], ["Value", 30]]],
    ["Left Arm", "", "images/inventory/armor_left_arm", "", [["PER", 1], ["Weight", 3], ["Value", 30]]],
    ["Right Arm", "", "images/inventory/armor_right_arm", "", [["PER", 1], ["Weight", 3], ["Value", 30]]],
    ["Left Leg", "", "images/inventory/armor_left_leg", "", [["PER", 1], ["Weight", 3], ["Value", 30]]],
    ["Right Leg", "", "images/inventory/armor_right_leg", "", [["PER", 1], ["Weight", 3], ["Value", 30]]],
    ["Wedding Ring", "", "images/inventory/armor_ring", "", [["Weight", 0], ["Value", 250]]],
]

FOOTER_ARMOR = ["WEIGHT 186/200", "CAPS: 35", "ARMOR: 50 / RADIATION: 1", None, False]

AID = [
    ["StimPak", 3, "images/inventory/stimpak",
     "A stimpak is an autoinjector loaded with a variety of healing medications and stimulants. By injecting the stimpak, one drastically increase one's own recuperative functions and gains lost hit points almost instantly."],
    ["Purified Water", 3, "images/inventory/purified_water",
     "A can of water, which has been cleansed of radiation. It restores 40 health."],
    ["RadAway", 2, "images/inventory/radaway",
     "RadAway is an intravenous chemical solution that bonds with radioactive particles and removes them from the user's system"],
]

FOOTER_AID = ["WEIGHT 186/200", "CAPS: 35", "HEALTH", 90, False]

MISC = [
    ["Pencil", 3, "images/inventory/pencil",
     "An orange pencil with a pink eraser. Use it to mark objects or poke eyes out."],
    ["Pre-War Money", 250, "images/inventory/prewarmoney", "Useless to all but time travelers. Can be used as tinder."],
    ["Wonderglue", 2, "images/inventory/wonderglue",
     "Joins this to that instantly. Will also bond fingers together faster than you can blink!"],
]

FOOTER_MISC = ["WEIGHT 20/200", "CAPS: 1", "", None, False]

AMMO = [
    ["10mm Rounds", 15, "images/inventory/10mmAmmo"],
    ["Fusion Cells", 28, "images/inventory/fusion_cells"],
]

FOOTER_TIME = ["DATE", "TIME", "", None, False]

QUESTS = [
    ["War Never Changes","","images/quests/war_never_changes","Get to Vault 111. Survive."],
    ["Out of Time","","images/quests/out_of_time",
     "While cryogenically frozen in Vault 111, I awoke just long enough to witness the murder of my wife/husband and the abduction of my infant son. I need to escape Vault 111 and return home, so I can begin to make sense of this tragedy."],
    ["Unlikely Valentine","","images/quests/unlikely_valentine",
     "Nick Valentine apparently went missing while investigating a case. If I want his help in locating Shaun, I'll need to find him first. His last known location was Park Street Station."],
    ["Reunions","","images/quests/reunions",
     "Kellogg is dead, and Shaun isn't here with him. I need to search around for some information that may lead me to my son."],
    ["The Glowing Sea","","images/quests/the_glowing_sea",
     "I need to find Virgil, the escaped Institute scientist, somewhere in the Glowing Sea and hope that he can help me reach the Institute."],
]

SKILLS = [
    ["Action Boy"],
    ["Animal Friend"],
    ["Awareness"],
    ["Gunslinger"],
    ["Hacker"],
    ["Mysterious Stranger"],
    ["Rifleman"],
    ["Science"],
]

PERKS = [
    ["Action Boy", 2, "images/perks/action_boy", "Your Action Points now regenerate 50% faster."],
    ["Animal Friend", 3, "images/perks/animal_friend",
     "When you successfully pacify an animal, you can give it specific commands."],
    ["Awareness", 1, "images/perks/awareness",
     "To defeat your enemies, know their weaknesses! You can view a target's specific damage resistances in V.A.T.S."],
    ["Blacksmith", 3, "images/perks/blacksmith",
     "Fire up the forge and gain access to base level and Rank 3 melee weapon mods."],
    ["Fortune Finder", 1, "images/perks/fortune_finder",
     "You've learned to discover the Wasteland's hidden wealth, and discover more bottle caps in containers."],
    ["Gunslinger", 1, "images/perks/gunslinger",
     "Channel the spirit of the old west! Non-automatic pistols do 20% more damage."],
    ["Hacker", 4, "images/perks/hacker", "When hacking, you never get locked out of a terminal when things go wrong."],
    ["Lone Wanderer", 2, "images/perks/lone_wanderer",
     "When adventuring without a companion, you take 30% less damage and carry weight increases by 100"],
    ["Mysterious Stranger", 1, "images/perks/mysterious_stranger",
     "Who is he? Why does he help? Who cares! The Mysterious Stranger will appear occasionally in V.A.T.S. to lend a hand, with deadly efficiency..."],
    ["Rifleman", 5, "images/perks/rifleman",
     "Attacks with non-automatic rifles do double damage and ignore 30% of a target's armor. They also have a slightly higher chance of crippling a limb."],
    ["Robotics Expert", 3, "images/perks/robotics_expert",
     "Machines will always serve humans, if you have anything to say about it. Hack a robot, and gain a chance to power it on or off, or initiate a self-destruct."],
    ["Sneak", 4, "images/perks/sneak",
     "Become whisper, become shadow. You are 50% harder to detect while sneaking."],
    ["Sniper",3,"images/perks/sniper/","It's all about focus. You have improved control and can hold your breath longer when aiming with scopes."],
]

# Detect if running on a Raspberry Pi
PI = False
if os.name == "posix":
    try:
        with open('/proc/device-tree/model', 'r') as f:
            PI = 'Raspberry' in f.read()
    except Exception:
        PI = True  # Assume Pi on any posix system without the model file

pygame.font.init()
RobotoB = {}
RobotoR = {}
TechMono = {}
for x in range(10, 34):
    RobotoB[x] = pygame.font.Font('fonts/RobotoCondensed-Bold.ttf', x)
    RobotoR[x] = pygame.font.Font('fonts/RobotoCondensed-Regular.ttf', x)
    TechMono[x] = pygame.font.Font('fonts/TechMono.ttf', x)

pygame.freetype.init()
FreeRobotoB = {}
FreeRobotoR = {}
FreeTechMono = {}
for x in range(10, 34):
    FreeRobotoB[x] = pygame.freetype.Font('fonts/RobotoCondensed-Bold.ttf', x)
    FreeRobotoR[x] = pygame.freetype.Font('fonts/RobotoCondensed-Regular.ttf', x)
    FreeTechMono[x] = pygame.freetype.Font('fonts/TechMono.ttf', x)

# Get and save volume and station setting
global VOLUME
try:
    VOLUME = float(saved.SAVED_VOLUME)
except:
    VOLUME = 0.5
global STATION
try:
    STATION = int(saved.SAVED_STATION)
except:
    STATION = 0

hide_top_menu = False
hide_submenu = False
hide_main_menu = False
hide_footer = False


def save_settings():
    file = open("saved.py", "w")
    file.write("SAVED_VOLUME = " + str(VOLUME) + "\n" + "SAVED_STATION = " + str(STATION))
    print("exiting", "SAVED_VOLUME = ", str(VOLUME), "SAVED_STATION = ", str(STATION))


atexit.register(save_settings)

# Glitch the screen up/down
glitch = False
glitch_time = 0.1
glitch_next = 0

# ─── Frame rate ───────────────────────────────────────────────────────────────
# 24 FPS is plenty for a Pip-Boy UI and keeps the Pi Zero 2W CPU relaxed.
# Raise to 30 if animations feel choppy; do NOT go above 30 on the Zero 2W.
frame_per_second = 24
fps_rate = (1 / frame_per_second)
# ─────────────────────────────────────────────────────────────────────────────

# Waveform related:
waveform_frequency = 48000  # All your OGG files should be this rate to keep things in sync
waveform_rate = 48
waveform_fps = int(frame_per_second / 2)
frame_skip = int(waveform_frequency / (waveform_fps * waveform_rate))

CURRENT_SONG = None

# Holotape related:
holotape_generic = "images/inventory/holotape"
