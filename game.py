
import cv2
import numpy as np
import random
import time

# =============================
# SETTINGS
# =============================
ROWS, COLS = 20, 10
CELL = 30

WIDTH = COLS * CELL
HEIGHT = ROWS * CELL
SIDE = 160  # side panel for score

DROP_DELAY = 0.5

# =============================
# SHAPES
# =============================
SHAPES = [
    [[1,1,1,1]],
    [[1,1],[1,1]],
    [[0,1,0],[1,1,1]],
    [[1,0,0],[1,1,1]],
    [[0,0,1],[1,1,1]]
]

COLORS = [
    (255,80,80),
    (80,255,80),
    (80,80,255),
    (255,255,80),
    (255,80,255)
]

# =============================
# GAME VARIABLES
# =============================
board = np.zeros((ROWS, COLS), dtype=int)
piece = random.choice(SHAPES)
color_id = random.randint(0, len(COLORS)-1)

px, py = 4, 0
score = 0
level = 1
last_drop = time.time()


# =============================
# DRAW GRID
# =============================
def draw_board(img):
    for r in range(ROWS):
        for c in range(COLS):

            cell = board[r][c]

            color = (25,25,25)
            if cell > 0:
                color = COLORS[cell-1]

            cv2.rectangle(img,
                          (c*CELL, r*CELL),
                          ((c+1)*CELL, (r+1)*CELL),
                          color, -1)

            cv2.rectangle(img,
                          (c*CELL, r*CELL),
                          ((c+1)*CELL, (r+1)*CELL),
                          (40,40,40), 1)


# =============================
# DRAW CURRENT PIECE
# =============================
def draw_piece(img):
    for i in range(len(piece)):
        for j in range(len(piece[0])):
            if piece[i][j]:
                x = px + j
                y = py + i
                cv2.rectangle(img,
                              (x*CELL, y*CELL),
                              ((x+1)*CELL, (y+1)*CELL),
                              COLORS[color_id], -1)


# =============================
# COLLISION CHECK
# =============================
def collision(nx, ny):
    for i in range(len(piece)):
        for j in range(len(piece[0])):
            if piece[i][j]:
                x = nx+j
                y = ny+i

                if x < 0 or x >= COLS or y >= ROWS:
                    return True

                if y >= 0 and board[y][x] > 0:
                    return True
    return False


# =============================
# LOCK PIECE
# =============================
def lock_piece():
    for i in range(len(piece)):
        for j in range(len(piece[0])):
            if piece[i][j]:
                board[py+i][px+j] = color_id+1


# =============================
# CLEAR ROWS + SCORE
# =============================
def clear_rows():
    global board, score, level

    new = []
    cleared = 0

    for row in board:
        if np.all(row > 0):
            cleared += 1
        else:
            new.append(row)

    for _ in range(cleared):
        new.insert(0, np.zeros(COLS))

    board[:] = new

    score += cleared * 100
    level = score // 500 + 1


# =============================
# ROTATE
# =============================
def rotate():
    global piece
    piece = np.rot90(piece)


# =============================
# GLITCH EFFECT
# =============================
def glitch(frame):
    noise = np.random.randint(0, 25, frame.shape, dtype='uint8')
    frame = cv2.add(frame, noise)

    if random.random() < 0.05:
        frame[:,:,0], frame[:,:,2] = frame[:,:,2], frame[:,:,0]

    return frame


# =============================
# MAIN LOOP
# =============================
while True:

    canvas = np.zeros((HEIGHT, WIDTH + SIDE, 3), dtype=np.uint8)

    speed = max(0.1, DROP_DELAY - level*0.03)

    # auto drop
    if time.time() - last_drop > speed:
        if not collision(px, py+1):
            py += 1
        else:
            lock_piece()
            clear_rows()

            piece = random.choice(SHAPES)
            color_id = random.randint(0, len(COLORS)-1)
            px, py = 4, 0

            if collision(px, py):
                break

        last_drop = time.time()

    draw_board(canvas)
    draw_piece(canvas)

    # ================= UI PANEL =================
    cv2.rectangle(canvas, (WIDTH, 0), (WIDTH+SIDE, HEIGHT), (15,15,15), -1)

    cv2.putText(canvas, "GLITCH FALL",
                (WIDTH+15, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

    cv2.putText(canvas, f"Score: {score}",
                (WIDTH+15, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

    cv2.putText(canvas, f"Level: {level}",
                (WIDTH+15, 160),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

    canvas = glitch(canvas)

    cv2.imshow("Glitch Fall", canvas)

    key = cv2.waitKey(1)

    if key == 27:
        break
    elif key == ord('a') and not collision(px-1, py):
        px -= 1
    elif key == ord('d') and not collision(px+1, py):
        px += 1
    elif key == ord('w'):
        rotate()

cv2.destroyAllWindows()
