import streamlit as st
from PIL import Image, ImageDraw, ImageFilter
import random

# — APP SETUP —
st.set_page_config(page_title="PxlSlyR Ultra-HD 2.0", layout="wide")
st.title("PxlSlyR: Epic 2D Pixel-Art Quest (Ultra-HD 2.0)")

# — CONFIGURATION —
GRID_W, GRID_H = 16, 8
TILE_PX       = 256   # Ultra-HD
SPR_PX        = 8     # native sprite res

# Map positions
CHEST        = (4, GRID_H-1)
FLAMWYRM     = (8, GRID_H-1)
CASTLE_ENTR  = (12,GRID_H-1)
DUNGEON_ENTR = (10,GRID_H-3)
PRISONERS    = [(DUNGEON_ENTR[0], DUNGEON_ENTR[1]),
                (DUNGEON_ENTR[0]+1, DUNGEON_ENTR[1])]
TOBY         = (2, GRID_H-2)
MIRRA        = (5, GRID_H-2)
ELISE_GUARD  = (9, 4)
FROSTFANG    = (7, 3)
GHOST        = (6, 2)
GOAL         = (12, 0)

# — THEMES & SIDEBAR —
themes = ["Day","Night","Autumn","Winter"]
theme  = st.sidebar.selectbox("🌈 Theme", themes, index=0)

characters = [
    ("Aric the Hero","You, the brave adventurer."),
    ("Flamwyrm","Fire beast at the gate."),
    ("Frostfang","Ice fiend in the halls."),
    ("Sir Rowan","Knight imprisoned."),
    ("Lady Elin","Ally locked away."),
    ("Princess Aria","Royal at the tower’s top."),
    ("Toby","Merchant with clues."),
    ("Mirra","Wise sage of riddles."),
    ("The Castle Ghost","Keeper of secrets."),
]
flow = [
    "Gear up & face Flamwyrm",
    "Enter castle & find key",
    "Free Sir Rowan & Lady Elin",
    "Learn secret passage",
    "Slay Frostfang",
    "Rescue Princess Aria",
]

with st.sidebar:
    st.header("📜 Characters")
    for n,d in characters:
        st.markdown(f"**{n}** — {d}")
    st.markdown("---")
    st.header("🎯 Quest Flow")
    for i,step in enumerate(flow,1):
        st.markdown(f"{i}. {step}")
    st.markdown("---")
    st.metric("🎉 Fun Meter", f"{st.session_state.get('fun',0)}%")
    st.metric("🎯 Moves",    st.session_state.get("moves",0))

# — SESSION STATE —
defaults = {
    "pos": [0,GRID_H-1],
    "stage":"start",
    "hp":3,
    "has_weapon":False,
    "flamwyrm_defeated":False,
    "key_found":False,
    "met_toby":False,
    "met_mirra":False,
    "prisoners":False,
    "met_ghost":False,
    "frostfang_defeated":False,
    "moves":0,
    "fun":0,
    "weather":[],
    "confetti":[],
    # —— Unicorn state —— 
    "unicorn_timer": random.randint(50,150),
    "unicorn_active": False,
    "unicorn_x": -1,
    "unicorn_y": 0,
    "unicorn_vx": TILE_PX // 8,
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# — PIXEL ART LOADING —
def load_sprite(pat, color):
    img = Image.new("RGBA",(SPR_PX,SPR_PX),(0,0,0,0))
    px = img.load()
    for y,row in enumerate(pat):
        for x,ch in enumerate(row):
            if ch=="X": px[x,y] = (*color,255)
    return img.resize((TILE_PX,TILE_PX),Image.NEAREST)

hero_pat     = ["........","..XX....",".XXXX...",".X.XX...",".XXXX...", "..X.X...","..XXX...","...X...."]
chest_pat    = ["........",".XXXXXX.","X.XXXX.X","X.XX.XX.","X.XXXX.X",".XXXXXX.","..XXXX..","........"]
monster_pat  = ["........","..XXXX..",".X.XX.X.",".XXXXX..","XXXXXXX.",".XXXXX..",".X...X..","..XXX..."]
princess_pat = ["........","..XXX...",".X.X.X..",".XXXXX..",".X.X.X..",".XXXXX..",".X...X..","...X...."]
castle_pat   = ["XXXXXXXX","X......X","X.XX.XX.","X.XX.XX.","X.XXXX.X","X.XXXX.X","X......X","XXXXXXXX"]
unicorn_pat  = ["........","...X....","..XXX...",".XXXXX..",".X.XX.X.",".XXXXXXX",".X.XX...", "....X..."]

hero_spr     = load_sprite(hero_pat,     (0,0,255))
chest_spr    = load_sprite(chest_pat,    (212,175,55))
flame_spr    = load_sprite(monster_pat,  (255,0,0))
frost_spr    = load_sprite(monster_pat,  (173,216,230))
princess_spr = load_sprite(princess_pat, (255,105,180))
castle_spr   = load_sprite(castle_pat,   (128,128,128))
unicorn_spr  = load_sprite(unicorn_pat,  (255,255,255))  # pure white unicorn

# — PARTICLE HELPERS —
def add_confetti(n=100):
    W,H = GRID_W*TILE_PX, GRID_H*TILE_PX
    for _ in range(n):
        st.session_state.confetti.append([
            random.randint(0,W), random.randint(0,H),
            random.choice(["red","orange","yellow","lime","cyan","magenta"]),
            random.randint(30,60)
        ])
def draw_confetti(d):
    new=[]
    for x,y,c,ttl in st.session_state.confetti:
        if ttl>0:
            r=random.randint(5,15)
            d.ellipse([x-r,y-r,x+r,y+r],fill=c)
            new.append([x,y,c,ttl-1])
    st.session_state.confetti=new

def add_weather(n=50):
    W,H = GRID_W*TILE_PX, GRID_H*TILE_PX
    for _ in range(n):
        st.session_state.weather.append([
            random.randint(0,W), 0,
            random.randint(2,6),
            random.choice(["snow","leaf","star"])
        ])
def draw_weather(d):
    new=[]
    for x,y,s,kind in st.session_state.weather:
        if y<H:
            if theme=="Winter" and kind=="snow":
                d.ellipse([x,y,x+s,y+s],fill="white")
            if theme=="Autumn" and kind=="leaf":
                d.rectangle([x,y,x+s,y+s//2],fill="orange")
            if theme=="Night" and kind=="star":
                d.point((x,y),fill="yellow")
            new.append([x,y+5,s,kind])
    st.session_state.weather=new

# — SCENE RENDERING —
def draw_scene():
    s=st.session_state
    W,H=GRID_W*TILE_PX,GRID_H*TILE_PX

    # background gradient
    bg=Image.new("RGB",(W,H))
    draw=ImageDraw.Draw(bg)
    for i in range(H//2):
        t=i/(H//2)
        if theme=="Night":
            col=(20+35*t,24+36*t,82+100*t)
        else:
            col=(135-20*t,206-6*t,235+20*t)
        draw.line([(0,i),(W,i)],fill=tuple(map(int,col)))

    # ground
    ground=(230,230,250) if theme=="Winter" else (34,139,34)
    draw.rectangle([0,H//2,W,H],fill=ground)

    # drifting clouds (if not night)
    if theme!="Night":
        offset=(s.moves*4)%(W+TILE_PX)-TILE_PX
        for cx in [2,6,12]:
            x=int(cx*TILE_PX+offset); y=int(TILE_PX*0.5)
            draw.ellipse([x,y,x+TILE_PX*2,y+TILE_PX*0.8],fill="white")
            draw.ellipse([x+TILE_PX*0.6,y-40,x+TILE_PX*2.6,y+TILE_PX*0.6],fill="white")

    # grid
    for i in range(GRID_W+1):
        draw.line([(i*TILE_PX,0),(i*TILE_PX,H)],fill="black")
    for j in range(GRID_H+1):
        draw.line([(0,j*TILE_PX),(W,j*TILE_PX)],fill="black")

    # chest sparkle when near
    px,py=s.pos
    if abs(px-CHEST[0])<2 and abs(py-CHEST[1])<2:
        for _ in range(30):
            x=random.randint(CHEST[0]*TILE_PX,(CHEST[0]+1)*TILE_PX)
            y=random.randint(CHEST[1]*TILE_PX,(CHEST[1]+1)*TILE_PX)
            draw.point((x,y),fill=random.choice(["yellow","white"]))

    # place sprites
    bg.paste(chest_spr,  (CHEST[0]*TILE_PX,CHEST[1]*TILE_PX), chest_spr)
    if not s.flamwyrm_defeated:
        bg.paste(flame_spr,(FLAMWYRM[0]*TILE_PX,FLAMWYRM[1]*TILE_PX),flame_spr)
    bg.paste(castle_spr, (CASTLE_ENTR[0]*TILE_PX,CASTLE_ENTR[1]*TILE_PX),castle_spr)

    # dungeon
    dx,dy=DUNGEON_ENTR
    draw.rectangle([dx*TILE_PX,dy*TILE_PX,(dx+2)*TILE_PX,(dy+1)*TILE_PX],fill="#552200")

    # NPC dots
    def dot(pos,col):
        x,y=pos
        draw.ellipse([x*TILE_PX+32,y*TILE_PX+32,(x+1)*TILE_PX-32,(y+1)*TILE_PX-32],fill=col)
    dot(TOBY,"orange"); dot(MIRRA,"purple"); dot(ELISE_GUARD,"grey")
    if s.met_ghost: dot(GHOST,"white")
    if s.stage in ("climb","secret") and not s.frostfang_defeated:
        bg.paste(frost_spr,(FROSTFANG[0]*TILE_PX,FROSTFANG[1]*TILE_PX),frost_spr)

    # prisoners
    if s.stage in ("rescue","secret","climb","done"):
        for x,y in PRISONERS:
            draw.rectangle([x*TILE_PX+64,y*TILE_PX+64,(x+1)*TILE_PX-64,(y+1)*TILE_PX-64],
                           fill="pink")
    # princess
    if s.stage in ("climb","done"):
        bg.paste(princess_spr,(GOAL[0]*TILE_PX,GOAL[1]*TILE_PX),princess_spr)

    # hero
    bg.paste(hero_spr,(px*TILE_PX,py*TILE_PX),hero_spr)

    # — draw the unicorn if active —
    if s.unicorn_active:
        uy = s.unicorn_y
        ux = s.unicorn_x
        bg.paste(unicorn_spr, (int(ux), int(uy)), unicorn_spr)

    # particles
    draw_weather(draw); draw_confetti(draw)
    return bg

# — GAME LOGIC & UNICORN SPAWN —
def move(dx, dy):
    s=st.session_state
    x,y=s.pos; nx,ny=x+dx,y+dy
    if not (0<=nx<GRID_W and 0<=ny<GRID_H): return
    s.pos=[nx,ny]; s.moves+=1; s.fun=min(100,s.fun+2)
    add_weather(5)

    # handle unicorn timer/spawn
    s.unicorn_timer -= 1
    if not s.unicorn_active and s.unicorn_timer <= 0:
        # spawn unicorn just off left edge
        s.unicorn_active = True
        s.unicorn_x = -TILE_PX
        s.unicorn_y = random.randint(0, GRID_H//2)*TILE_PX
        # reset timer
        s.unicorn_timer = random.randint(100,300)
    # move unicorn if active
    if s.unicorn_active:
        s.unicorn_x += s.unicorn_vx
        # de-spawn when off right edge
        if s.unicorn_x > GRID_W*TILE_PX:
            s.unicorn_active = False

    # quest logic (unchanged from Ultra-HD 2.0)...
    # [ ... include all the existing stage checks & add_confetti() calls ... ]

    # For brevity, assume you copy over all the same interactions
    # from the previous Ultra-HD 2.0 move() here.

# — RENDER & CONTROLS —
st.image(draw_scene(), use_column_width=True)
c1,c2,c3 = st.columns(3)
if c1.button("⬅️"): move(-1,0)
if c2.button("⬆️"): move(0,-1)
if c3.button("➡️"): move(1,0)
if st.button("⬇️"): move(0,1)
