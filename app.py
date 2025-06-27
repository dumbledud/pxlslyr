import streamlit as st
from PIL import Image, ImageDraw

# — APP TITLE —————————————————————————————————————————————————————
st.set_page_config(page_title="PxlSlyR", layout="wide")
st.title("PxlSlyR: Epic 2D Pixel-Art Quest")

# — CONFIGURATION —————————————————————————————————————————————————————
GRID_W, GRID_H = 16, 8       # grid dimensions (cells)
TILE_PX     = 32             # pixels per cell

# Key map locations
CHEST         = (4, GRID_H - 1)
FLAMWYRM      = (8, GRID_H - 1)
CASTLE_ENTR   = (12, GRID_H - 1)
DUNGEON_ENTR  = (10, GRID_H - 3)
PRISONERS     = [(DUNGEON_ENTR[0], DUNGEON_ENTR[1]), (DUNGEON_ENTR[0]+1, DUNGEON_ENTR[1])]
TOBY          = (2, GRID_H - 2)
MIRRA         = (5, GRID_H - 2)
ELISE_GUARD   = (9, 4)
FROSTFANG     = (7, 3)
GHOST         = (6, 2)
GOAL          = (12, 0)  # Princess Aria

# — CHARACTER & FLOW DEFINITIONS ———————————————————————————————————————
characters = [
    ("Aric the Hero",            "Brave adventurer (you)."),
    ("Flamwyrm",                 "Fire monster at the gate."),
    ("Frostfang",                "Ice monster in the corridors."),
    ("Sir Rowan",                "Noble knight imprisoned."),
    ("Lady Elin",                "Courageous ally locked away."),
    ("Princess Aria",            "Royal maiden atop the tower."),
    ("King Roland",              "Absent ruler, Aria’s father."),
    ("Queen Marisol",            "Her portrait holds a clue."),
    ("Gorak the Dungeon Keeper", "Ruthless warden."),
    ("Elise the Guard",          "Vigilant sentinel."),
    ("Toby the Merchant",        "Trader with key hints."),
    ("Brenn the Blacksmith",     "Forge-master of your sword."),
    ("Mirra the Old Sage",       "Riddle-spewing wise woman."),
    ("The Castle Ghost",         "Spectral secret-keeper.")
]

flow_steps = [
    "Open the chest to equip armor & sword.",
    "Battle Flamwyrm with your new gear.",
    "Enter the castle; seek the dungeon key.",
    "Talk to Toby & Mirra; discover hidden key.",
    "Unlock dungeon; free Rowan & Elin.",
    "Consult the Castle Ghost for a passage clue.",
    "Sneak past Elise & slay Frostfang.",
    "Climb the spiral staircase to the top.",
    "Rescue Princess Aria and celebrate!"
]

# — SESSION STATE SETUP —————————————————————————————————————————————————
if "pos" not in st.session_state:
    st.session_state.pos = [0, GRID_H - 1]

defaults = {
    "has_weapon": False,
    "hp": 3,
    "stage": "start",        # start → explore → key_search → rescue → secret → climb → done
    "key_found": False,
    "prisoners_rescued": False,
    "flamwyrm_defeated": False,
    "frostfang_defeated": False,
    "met_toby": False,
    "met_mirra": False,
    "met_ghost": False,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# — PIXEL-ART SPRITES LOADING ————————————————————————————————————————
SPR_PX = 8  # native sprite resolution

# simple patterns reused from earlier versions...
hero_pat = [
    "........",
    "..XXX...",
    ".XXXXX..",
    ".X.XX.X.",
    ".XXXXX..",
    "..X.X...",
    "..XXX...",
    "...X....",
]
chest_pat = [
    "........",
    ".XXXXXX.",
    "X.XX.XX.",
    "X.XXXX.X",
    "X.XX.XX.",
    "X.XXXX.X",
    ".XXXXXX.",
    "..XXXX..",
]
monster_pat = [
    "........",
    "..XXXX..",
    ".X.XX.X.",
    ".XXXXX..",
    "XXXXXXX.",
    ".XXXXX..",
    ".X...X..",
    "..XXX...",
]
princess_pat = [
    "........",
    "..XXX...",
    ".X.X.X..",
    ".XXXXX..",
    ".X.X.X..",
    ".XXXXX..",
    ".X...X..",
    "...X....",
]
castle_pat = [
    "XXXXXXXX",
    "X......X",
    "X.XX.XX.",
    "X.XX.XX.",
    "X......X",
    "X.XXXX.X",
    "X......X",
    "XXXXXXXX",
]

def load_sprite(pattern, rgb):
    img = Image.new("RGBA", (SPR_PX, SPR_PX), (0,0,0,0))
    px = img.load()
    for y,row in enumerate(pattern):
        for x,ch in enumerate(row):
            if ch == "X":
                px[x,y] = (*rgb,255)
    return img.resize((TILE_PX, TILE_PX), Image.NEAREST)

# create scaled sprites
hero_spr    = load_sprite(hero_pat,    (0,0,255))
chest_spr   = load_sprite(chest_pat,   (212,175,55))
flame_spr   = load_sprite(monster_pat, (255,0,0))
frost_spr   = load_sprite(monster_pat, (173,216,230))
princess_spr= load_sprite(princess_pat,(255,105,180))
castle_spr  = load_sprite(castle_pat,  (128,128,128))

# — DRAWING FUNCTION ——————————————————————————————————————————————————
def draw_scene():
    img = Image.new("RGB", (GRID_W*TILE_PX, GRID_H*TILE_PX), "skyblue")
    d   = ImageDraw.Draw(img)
    # grass floor
    d.rectangle([0, GRID_H//2*TILE_PX, GRID_W*TILE_PX, GRID_H*TILE_PX], fill="#228B22")
    # grid lines
    for i in range(GRID_W+1):
        d.line([(i*TILE_PX,0),(i*TILE_PX,GRID_H*TILE_PX)], fill="black")
    for j in range(GRID_H+1):
        d.line([(0,j*TILE_PX),(GRID_W*TILE_PX,j*TILE_PX)], fill="black")

    s = st.session_state

    # draw chest
    img.paste(chest_spr, (CHEST[0]*TILE_PX, CHEST[1]*TILE_PX), chest_spr)

    # draw Flamwyrm if alive
    if not s.flamwyrm_defeated:
        img.paste(flame_spr, (FLAMWYRM[0]*TILE_PX, FLAMWYRM[1]*TILE_PX), flame_spr)

    # castle entrance
    img.paste(castle_spr, (CASTLE_ENTR[0]*TILE_PX, CASTLE_ENTR[1]*TILE_PX), castle_spr)

    # dungeon entrance
    dx,dy = DUNGEON_ENTR
    d.rectangle([dx*TILE_PX, dy*TILE_PX, (dx+2)*TILE_PX, (dy+1)*TILE_PX], fill="#552200")

    # NPCs
    def circle_sprite(pos, color):
        x,y = pos
        d.ellipse([x*TILE_PX+10,y*TILE_PX+10,(x+1)*TILE_PX-10,(y+1)*TILE_PX-10], fill=color)
    circle_sprite(TOBY,       "orange")
    circle_sprite(MIRRA,      "purple")
    circle_sprite(ELISE_GUARD,"grey")
    if s.met_ghost:
        circle_sprite(GHOST,    "white")
    if not s.frostfang_defeated and s.stage in ("secret","climb"):
        img.paste(frost_spr, (FROSTFANG[0]*TILE_PX, FROSTFANG[1]*TILE_PX), frost_spr)

    # prisoners appear once unlocked
    if s.stage in ("rescue","secret","climb","done"):
        for px,py in PRISONERS:
            d.rectangle([px*TILE_PX+12,py*TILE_PX+12,(px+1)*TILE_PX-12,(py+1)*TILE_PX-12], fill="pink")

    # princess at goal
    if s.stage in ("climb","done"):
        img.paste(princess_spr, (GOAL[0]*TILE_PX, GOAL[1]*TILE_PX), princess_spr)

    # hero
    hx,hy = s.pos
    img.paste(hero_spr, (hx*TILE_PX, hy*TILE_PX), hero_spr)

    return img

# — GAME LOGIC ———————————————————————————————————————————————————————
def move(dx, dy):
    s = st.session_state
    x,y = s.pos
    nx,ny = x+dx, y+dy
    if not (0<=nx<GRID_W and 0<=ny<GRID_H):
        return
    s.pos = [nx,ny]

    # stage progression
    if s.stage == "start":
        s.stage = "explore"
        st.info("Stage 1: Explore & defeat Flamwyrm")

    # equip from chest
    if s.stage=="explore" and (nx,ny)==CHEST and not s.has_weapon:
        s.has_weapon = True
        st.success("🛡️ You equipped armor & sword!")

    # fight Flamwyrm
    if s.stage=="explore" and (nx,ny)==FLAMWYRM and not s.flamwyrm_defeated:
        if s.has_weapon:
            s.flamwyrm_defeated = True
            st.success("🔥 Flamwyrm defeated!")
        else:
            s.hp -= 1
            st.error("💥 You were burned! -1 HP")
            if s.hp<=0:
                st.error("💀 You died. Respawning...")
                s.hp = 3
                s.pos = [0, GRID_H-1]
                return

    # enter castle if boss down
    if s.stage=="explore" and (nx,ny)==CASTLE_ENTR and s.flamwyrm_defeated:
        s.stage = "key_search"
        st.success("🏰 Entered castle. Find the dungeon key!")

    # meet NPCs for clues
    if s.stage=="key_search":
        if (nx,ny)==TOBY and not s.met_toby:
            s.met_toby = True
            st.info("Toby: 'They hid the key behind the queen’s portrait.'")
        if (nx,ny)==MIRRA and not s.met_mirra:
            s.met_mirra = True
            st.info("Mirra: 'Find Brenn’s mark in the armory.'")
        if s.met_toby and s.met_mirra and not s.key_found:
            s.key_found = True
            st.success("🗝️ You discovered the dungeon key!")

    # unlock dungeon
    if s.stage=="key_search" and (nx,ny)==DUNGEON_ENTR and s.key_found:
        s.stage = "rescue"
        st.success("🔓 Dungeon unlocked! Rescue your allies!")

    # rescue prisoners
    if s.stage=="rescue" and (nx,ny) in PRISONERS and not s.prisoners_rescued:
        s.prisoners_rescued = True
        st.success("🤝 Sir Rowan & Lady Elin rescued!")
        s.stage="secret"
        st.info("🔦 Seek the Castle Ghost for a secret.")

    # ghost reveals passage
    if s.stage=="secret" and (nx,ny)==GHOST and not s.met_ghost:
        s.met_ghost = True
        st.success("👻 Ghost: 'Through the guard’s quarters, head west then north.'")
        s.stage = "climb"

    # Frostfang fight
    if s.stage=="climb" and (nx,ny)==FROSTFANG and not s.frostfang_defeated:
        if s.has_weapon:
            s.frostfang_defeated = True
            st.success("❄️ Frostfang slain!")
        else:
            s.hp -= 1
            st.error("🧊 You froze! -1 HP")
            if s.hp<=0:
                st.error("💀 You froze solid. Restarting climb...")
                s.hp = 3
                s.pos = [CASTLE_ENTR[0], CASTLE_ENTR[1]-1]
                return

    # final rescue
    if s.stage=="climb" and (nx,ny)==GOAL:
        s.stage="done"
        st.balloons()
        st.success("👑 Princess Aria is safe. You win!")

# — UI LAYOUT ———————————————————————————————————————————————————————
# Sidebar with character list and flow
with st.sidebar:
    st.header("📜 Characters")
    for name,desc in characters:
        st.markdown(f"**{name}** — {desc}")
    st.markdown("---")
    st.header("🎯 Quest Flow")
    for i,step in enumerate(flow_steps,1):
        st.markdown(f"{i}. {step}")

# Main game view
st.image(draw_scene(), use_column_width=True)

# Movement controls
c1,c2,c3 = st.columns(3)
if c1.button("⬅️"): move(-1,0)
if c2.button("⬆️"): move(0,-1)
if c3.button("➡️"): move(1,0)
if st.button("⬇️"): move(0,1)

# Status panel
s = st.session_state
st.markdown(
    f"**Stage:** {s.stage}  \n"
    f"**Weapon:** {'✓' if s.has_weapon else '✗'}  \n"
    f"**HP:** {'❤️'*s.hp}{'🤍'*(3-s.hp)}  \n"
    f"**Key Found:** {'✓' if s.key_found else '✗'}  \n"
    f"**Rescued:** {'✓' if s.prisoners_rescued else '✗'}  \n"
    f"**Flamwyrm:** {'✓' if s.flamwyrm_defeated else '✗'}  \n"
    f"**Frostfang:** {'✓' if s.frostfang_defeated else '✗'}"
)
