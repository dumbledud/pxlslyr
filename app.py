import streamlit as st
from PIL import Image, ImageDraw

# — CONFIG —————————————————————————————————————————————————————
GRID_W, GRID_H = 16, 8         # cells
TILE_PX     = 32               # pixels per cell
SPR_PX      = 8                # sprite’s native resolution
SCALE       = TILE_PX // SPR_PX

# key locations
CHEST   = (4, GRID_H-1)
MONSTER = (8, GRID_H-1)
CASTLE  = (12, GRID_H-1)
GOAL    = (12, 0)

# — PIXEL ART PATTERNS ———————————————————————————————————————
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

def load_sprite(pattern, rgb):
    img = Image.new("RGBA", (SPR_PX, SPR_PX), (0, 0, 0, 0))
    px = img.load()
    for y, row in enumerate(pattern):
        for x, ch in enumerate(row):
            if ch == "X":
                px[x, y] = (*rgb, 255)
    return img.resize((TILE_PX, TILE_PX), Image.NEAREST)

# load sprites
hero    = load_sprite(hero_pat,    (  0,   0, 255))
chest   = load_sprite(chest_pat,   (212, 175,  55))
monster = load_sprite(monster_pat, (255,   0,   0))
castle  = load_sprite(castle_pat,  (128, 128, 128))
princess= load_sprite(princess_pat,(255, 192, 203))

# — SESSION STATE —————————————————————————————————————————————
if "pos" not in st.session_state:
    st.session_state.pos = [0, GRID_H-1]
if "has_weapon" not in st.session_state:
    st.session_state.has_weapon = False
if "monster_alive" not in st.session_state:
    st.session_state.monster_alive = True
if "hp" not in st.session_state:
    st.session_state.hp = 3
if "stage" not in st.session_state:
    st.session_state.stage = "explore"  # explore → climb → done

# — GAME LOGIC —————————————————————————————————————————————
def move(dx, dy):
    x, y = st.session_state.pos
    nx, ny = x + dx, y + dy
    if not (0 <= nx < GRID_W and 0 <= ny < GRID_H):
        return
    st.session_state.pos = [nx, ny]

    # 1) pick up chest
    if st.session_state.stage=="explore" and (nx, ny)==CHEST:
        st.session_state.has_weapon = True
        st.success("🗡️ You found the weapon!")
    # 2) fight monster
    if st.session_state.stage=="explore" and (nx, ny)==MONSTER and st.session_state.monster_alive:
        if st.session_state.has_weapon:
            st.session_state.monster_alive = False
            st.success("🔥 You slayed the fire monster!")
        else:
            st.session_state.hp -= 1
            st.error("💥 You got burned! Lose 1 HP.")
            if st.session_state.hp <= 0:
                st.error("💀 You died! Restarting...")
                st.session_state.pos = [0, GRID_H-1]
                st.session_state.hp = 3
    # 3) enter castle
    if (nx, ny)==CASTLE and st.session_state.stage=="explore" and not st.session_state.monster_alive:
        st.session_state.stage = "climb"
        st.success("🏰 You enter the castle! Climb up!")
    # 4) rescue princess
    if (nx, ny)==GOAL and st.session_state.stage=="climb":
        st.session_state.stage = "done"
        st.balloons()
        st.success("👑 You rescued the princess!")

# — RENDER —————————————————————————————————————————————————————
def draw_scene():
    img = Image.new("RGB", (GRID_W*TILE_PX, GRID_H*TILE_PX), "skyblue")
    d = ImageDraw.Draw(img)
    # grass row
    for row in range(GRID_H//2, GRID_H):
        y0 = row * TILE_PX
        d.rectangle([0, y0, GRID_W*TILE_PX, GRID_H*TILE_PX], fill="#228B22")

    # grid lines
    for i in range(GRID_W+1):
        d.line([(i*TILE_PX,0),(i*TILE_PX,GRID_H*TILE_PX)], fill="black")
    for j in range(GRID_H+1):
        d.line([(0,j*TILE_PX),(GRID_W*TILE_PX,j*TILE_PX)], fill="black")

    # draw sprites
    if st.session_state.stage=="explore":
        img.paste(chest,   (CHEST[0]*TILE_PX,   CHEST[1]*TILE_PX),   chest)
        if st.session_state.monster_alive:
            img.paste(monster,(MONSTER[0]*TILE_PX, MONSTER[1]*TILE_PX), monster)
    # castle & walls
    img.paste(castle, (CASTLE[0]*TILE_PX, CASTLE[1]*TILE_PX), castle)
    if st.session_state.stage in ("climb","done"):
        x0 = CASTLE[0]*TILE_PX
        x1 = (CASTLE[0]+1)*TILE_PX
        d.line([(x0,0),(x0,GRID_H*TILE_PX)], fill="black", width=3)
        d.line([(x1,0),(x1,GRID_H*TILE_PX)], fill="black", width=3)
        img.paste(princess,(GOAL[0]*TILE_PX, GOAL[1]*TILE_PX), princess)

    # hero
    px, py = st.session_state.pos
    img.paste(hero, (px*TILE_PX, py*TILE_PX), hero)

    return img

# — UI —————————————————————————————————————————————————————————
st.title("🗡️ Advanced Pixel-Art 2D Adventure")
st.image(draw_scene())

# movement controls
c1, c2, c3 = st.columns([1,1,1])
if c1.button("⬅️"): move(-1,0)
if c2.button("⬆️"): move(0,-1)
if c3.button("➡️"): move(1,0)
if st.button("⬇️"): move(0,1)

# status
st.markdown(
    f"**Stage:** {st.session_state.stage}  \n"
    f"**Weapon:** {'✓' if st.session_state.has_weapon else '✗'}  \n"
    f"**Monster Alive:** {'✓' if st.session_state.monster_alive else '✗'}  \n"
    f"**HP:** {'❤️'*st.session_state.hp}{'🤍'*(3-st.session_state.hp)}"
)
