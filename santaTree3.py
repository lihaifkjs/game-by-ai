import math
import random
import pygame

# ================== 全局参数 ==================
WIDTH, HEIGHT = 1600, 900

GROUND_POINTS = 4000
STAR_POINTS   = 1200
HEART_POINTS  = 1000
SNOW2D_POINTS = 12

CAM_DIST   = 18.0
CAM_HEIGHT = 6.0
PITCH      = -0.25

TREE_HEIGHT = 12.0

rot_angle = 0.0
auto_rotate = True
auto_speed = 0.45
drag_speed = 0.004
is_drag = False
last_mouse_x = 0

zoom = 1.0
zoom_min = 0.4
zoom_max = 2.6

# 树冠Y区间：叶子仅在这些高度生成
crown_zones = [
    {"y0": 1.8, "y1": 2.4},
    {"y0": 4.4, "y1": 4.8},
    {"y0": 6.6, "y1": 7.0},
    {"y0": 8.2, "y1": 8.6},
    {"y0": 9.4, "y1": 9.8},
]

def is_in_crown(y):
    for zone in crown_zones:
        if zone["y0"] <= y <= zone["y1"]:
            return True
    return False


# ================== 生成树干：尺寸保持不变 ==================
def gen_trunk_points():
    pts = []
    trunk_segs = [
        {"y0": 0.0, "y1": 2.4, "r": 0.55, "cnt": 4000},
        {"y0": 2.4, "y1": 4.4, "r": 0.45, "cnt": 3000},
        {"y0": 4.4, "y1": 6.6, "r": 0.35, "cnt": 2500},
        {"y0": 6.6, "y1": 8.2, "r": 0.28, "cnt": 2000},
        {"y0": 8.2, "y1": 9.4, "r": 0.20, "cnt": 1500},
        # 顶部连接段保持不变
        {"y0": 9.4, "y1": 10.0, "r": 0.12, "cnt": 800},
    ]

    for seg in trunk_segs:
        y0 = seg["y0"]
        y1 = seg["y1"]
        r = seg["r"]
        count = seg["cnt"]
        for _ in range(count):
            y = random.uniform(y0, y1)
            rr = r * math.sqrt(random.random())
            angle = random.random() * math.tau

            x = math.cos(angle) * rr
            z = math.sin(angle) * rr

            color = [90 + random.randint(-10, 15), 70 + random.randint(-8, 12), 60]
            pts.append([x, y, z, color, 0, 0])
    return pts


# ================== 生成树枝：树冠间隔拉开 ==================
def gen_tree_points():
    pts = []

    # 每层y_base同步上移或下移，拉开间隔
    layers = [
        {"y_base": 2.1, "branch_len": 6.2, "branch_count": 14, "side_branch": 4, "leaf_num": 192, "extra_clusters": 4},
        {"y_base": 4.6, "branch_len": 4.8, "branch_count": 12, "side_branch": 3, "leaf_num": 160, "extra_clusters": 3},
        {"y_base": 6.8, "branch_len": 3.6, "branch_count": 10, "side_branch": 3, "leaf_num": 144, "extra_clusters": 3},
        {"y_base": 8.4, "branch_len": 2.6, "branch_count": 8,  "side_branch": 2, "leaf_num": 112, "extra_clusters": 2},
        {"y_base": 9.6, "branch_len": 1.4, "branch_count": 6,  "side_branch": 2, "leaf_num": 96,  "extra_clusters": 2},
    ]

    for layer in layers:
        y0 = layer["y_base"]
        blen = layer["branch_len"]
        bnum = layer["branch_count"]
        sidenum = layer["side_branch"]
        leaf_num = layer["leaf_num"]
        extra_clusters = layer["extra_clusters"]

        for bi in range(bnum):
            ang = (bi / bnum) * math.tau
            dir_x = math.cos(ang)
            dir_z = math.sin(ang)
            dir_y = 0.22

            seg_count = 10
            for si in range(seg_count):
                t = si / seg_count
                px = dir_x * blen * t
                py = y0 + dir_y * blen * t
                pz = dir_z * blen * t

                pts.append([px, py, pz, [70, 55, 45], 0, 0])

                for sid in range(sidenum):
                    side_ang = random.uniform(-0.6, 0.6)
                    side_t = random.uniform(0.2, 0.95)
                    spx = dir_x * blen * side_t
                    spy = y0 + dir_y * blen * side_t
                    spz = dir_z * blen * side_t

                    sx = spx + math.cos(ang + side_ang) * random.uniform(0.45, 1.0)
                    sz = spz + math.sin(ang + side_ang) * random.uniform(0.45, 1.0)
                    sy = spy + random.uniform(-0.3, 0.4)

                    for _ in range(leaf_num):
                        ox = random.uniform(-0.36, 0.36)
                        oy = random.uniform(-0.36, 0.36)
                        oz = random.uniform(-0.36, 0.36)
                        lx = sx + ox
                        ly = sy + oy
                        lz = sz + oz

                        if not is_in_crown(ly):
                            continue

                        rv = 140 + random.randint(-10, 20)
                        gv = 210 + random.randint(-10, 20)
                        bv = 255
                        color = [rv, gv, bv]
                        is_light = 1 if random.random() < 0.07 else 0
                        phase = random.uniform(0, math.tau)
                        if is_light:
                            color = [255, 255, 255]
                        pts.append([lx, ly, lz, color, is_light, phase])

            for _ in range(extra_clusters):
                cluster_r = random.uniform(0.6, 1.6)
                cluster_ang = random.uniform(0, math.tau)
                cluster_x = math.cos(cluster_ang) * cluster_r
                cluster_z = math.sin(cluster_ang) * cluster_r
                cluster_y = y0 + random.uniform(-0.25, 0.25)

                for __ in range(32):
                    lx = cluster_x + random.uniform(-0.36, 0.36)
                    ly = cluster_y + random.uniform(-0.12, 0.12)
                    lz = cluster_z + random.uniform(-0.36, 0.36)

                    if not is_in_crown(ly):
                        continue

                    rv = 140 + random.randint(-10, 20)
                    gv = 210 + random.randint(-10, 20)
                    bv = 255
                    color = [rv, gv, bv]
                    is_light = 1 if random.random() < 0.07 else 0
                    phase = random.uniform(0, math.tau)
                    if is_light:
                        color = [255, 255, 255]
                    pts.append([lx, ly, lz, color, is_light, phase])

    tip_count = 12000
    for _ in range(tip_count):
        h = random.random() ** 1.8
        y = 10 + h * 2.0
        r = (1 - h) * 0.8
        ang = random.random() * math.tau
        x = math.cos(ang) * r
        z = math.sin(ang) * r

        rv = 140 + random.randint(-10, 20)
        gv = 210 + random.randint(-10, 20)
        bv = 255
        color = [rv, gv, bv]
        is_light = 1 if random.random() < 0.11 else 0
        phase = random.uniform(0, math.tau)
        if is_light:
            color = [255, 255, 255]
        pts.append([x, y, z, color, is_light, phase])

    return pts


# ================== 地面光环 ==================
def gen_ground_points():
    pts = []
    rings = [4.6, 6.0, 7.4, 8.8, 10.2, 11.4]
    for _ in range(GROUND_POINTS):
        ring = random.choice(rings)
        r = random.gauss(ring, 0.3)
        theta = random.random() * math.tau
        x = math.cos(theta) * r
        z = math.sin(theta) * r
        y = -0.25

        if random.random() < 0.15:
            c = random.randint(235, 255)
        else:
            c = random.randint(190, 235)
        color = [c, c, 255]

        is_light = 1 if random.random() < 0.25 else 0
        light_phase = random.uniform(0, math.tau)

        pts.append([x, y, z, color, is_light, light_phase])
    return pts


# ================== 空中亮点 ==================
def gen_star_points():
    pts = []
    for _ in range(STAR_POINTS):
        x = random.uniform(-18.0, 18.0)
        z = random.uniform(-18.0, 18.0)
        y = random.uniform(3.0, 18.0)
        base = random.randint(215, 255)
        color = [base, base, 255]

        is_light = 1 if random.random() < 0.35 else 0
        light_phase = random.uniform(0, math.tau)

        pts.append([x, y, z, color, is_light, light_phase])
    return pts


# ================== 树顶爱心 ==================
def gen_heart_points():
    pts = []
    scale = 0.9
    top_y = 12.0

    while len(pts) < HEART_POINTS:
        x = random.uniform(-1.3, 1.3)
        y = random.uniform(-1.4, 1.4)

        f = (x * x + y * y - 1.0) ** 3 - x * x * (y ** 3)

        if f <= 0.0:
            wx = x * scale * 0.8
            wy = top_y + (y + 1.0) * scale * 0.5
            wz = random.uniform(-0.18, 0.18)

            dist = math.hypot(x, y)
            factor = max(0.35, 1.15 - 0.5 * dist)

            r = min(255, int(160 + 60 * factor))
            g = min(255, int(220 + 35 * factor))
            b = 255

            color = [r, g, b]
            is_light = 1 if random.random() < 0.5 else 0
            light_phase = random.uniform(0, math.tau)

            pts.append([wx, wy, wz, color, is_light, light_phase])

    return pts


# ================== 前景大雪花 ==================
def init_snow2d():
    flakes = []
    for _ in range(SNOW2D_POINTS):
        x = random.uniform(0, WIDTH)
        y = random.uniform(-80, -10)
        radius = random.uniform(10.0, 16.0)
        speed = random.uniform(30.0, 45.0)
        travel = HEIGHT + 80 - y
        life = travel / speed
        max_life = life
        flakes.append([x, y, radius, speed, life, max_life])
    return flakes


def respawn_flake(f):
    x = random.uniform(0, WIDTH)
    y = random.uniform(-80, -10)
    radius = random.uniform(10.0, 16.0)
    speed = random.uniform(30.0, 45.0)
    travel = HEIGHT + 80 - y
    life = travel / speed
    max_life = life
    f[0], f[1], f[2], f[3], f[4], f[5] = x, y, radius, speed, life, max_life


def update_snow2d(flakes, dt):
    for f in flakes:
        x, y, r, v, life, max_life = f
        y += v * dt
        life -= dt
        if life <= 0 or y > HEIGHT + 50:
            respawn_flake(f)
        else:
            f[0], f[1], f[4] = x, y, life


def draw_snow2d(surface, flakes):
    surface.fill((0, 0, 0, 0))
    for x, y, r, v, life, max_life in flakes:
        if max_life <= 0:
            continue

        phase = life / max_life
        if phase > 0.3:
            alpha = 255
        else:
            alpha = int(255 * (phase / 0.3))
        alpha = max(0, min(255, alpha))

        cx, cy = int(x), int(y)

        r1 = max(1, int(r * 1.3))
        r2 = max(1, int(r * 1.0))
        r3 = max(1, int(r * 0.75))
        r4 = max(1, int(r * 0.55))
        r5 = max(1, int(r * 0.45))

        a1 = alpha // 20
        a2 = alpha // 12
        a3 = alpha // 6
        a4 = alpha // 3
        a5 = alpha

        if a1 > 0:
            pygame.draw.circle(surface, (255, 255, 255, a1), (cx, cy), r1)
        if a2 > 0:
            pygame.draw.circle(surface, (255, 255, 255, a2), (cx, cy), r2)
        if a3 > 0:
            pygame.draw.circle(surface, (255, 255, 255, a3), (cx, cy), r3)
        if a4 > 0:
            pygame.draw.circle(surface, (255, 255, 255, a4), (cx, cy), r4)

        pygame.draw.circle(surface, (255, 255, 255, a5), (cx, cy), r5)


# ================== 3D 投影 ==================
def project_point(x, y, z, angle, current_zoom):
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    xz = x * cos_a - z * sin_a
    zz = x * sin_a + z * cos_a

    cos_p = math.cos(PITCH)
    sin_p = math.sin(PITCH)
    yp = y * cos_p - zz * sin_p
    zp = y * sin_p + zz * cos_p

    zp = zp + CAM_DIST
    yp = yp - CAM_HEIGHT

    if zp <= 0.1:
        return None

    f = (HEIGHT * 0.63 * current_zoom) / zp
    sx = int(WIDTH / 2 + xz * f)
    sy = int(HEIGHT / 2 - yp * f)
    depth = zp
    return sx, sy, depth


# ================== 背景暗辉光 ==================
def draw_bg_glow(screen, t):
    screen.fill((2, 4, 18))

    cx = WIDTH // 2
    cy = HEIGHT // 2
    base_radius = 380
    pulse = 1 + 0.03 * math.sin(t * 0.6)

    for i in range(10, 0, -1):
        ratio = i / 10
        radius = int(base_radius * ratio * pulse)
        alpha = int(14 * (1 - ratio) ** 1.8)
        if alpha <= 0:
            continue
        color = (
            int(10 + 6 * ratio),
            int(14 + 10 * ratio),
            int(30 + 22 * ratio),
            alpha
        )
        pygame.draw.circle(screen, color, (cx, cy), radius)

    corners = [
        (60, 70, 160, 22),
        (WIDTH - 60, 70, 160, 22),
        (60, HEIGHT - 70, 150, 20),
        (WIDTH - 60, HEIGHT - 70, 150, 20),
    ]
    for (x, y, r, a) in corners:
        pygame.draw.circle(screen, (18, 28, 70, a), (x, y), r)


# ================== 主循环 ==================
def main():
    global rot_angle, auto_rotate, is_drag, last_mouse_x, zoom

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Merry Christmas | Drag to rotate, Wheel to zoom, Space to toggle auto")
    clock = pygame.time.Clock()
    font_big = pygame.font.SysFont("Monotype Corsiva", 52, bold=False)
    font_small = pygame.font.SysFont("Arial", 22)

    print("Generating tree...")
    trunk = gen_trunk_points()
    tree = gen_tree_points()
    ground = gen_ground_points()
    stars = gen_star_points()
    heart = gen_heart_points()
    snow2d = init_snow2d()
    snow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    print(f"Tree points: {len(tree)}, Trunk points: {len(trunk)}")

    t = 0.0
    running = True

    while running:
        dt_ms = clock.tick(60)
        dt = dt_ms / 1000.0
        t += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    is_drag = True
                    last_mouse_x = event.pos[0]
                elif event.button == 4:
                    zoom = min(zoom_max, zoom * 1.08)
                elif event.button == 5:
                    zoom = max(zoom_min, zoom / 1.08)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                is_drag = False

            if event.type == pygame.MOUSEMOTION and is_drag:
                dx = event.pos[0] - last_mouse_x
                rot_angle += dx * drag_speed
                last_mouse_x = event.pos[0]

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    auto_rotate = not auto_rotate

        if auto_rotate and not is_drag:
            rot_angle += auto_speed * dt

        draw_bg_glow(screen, t)
        update_snow2d(snow2d, dt)   # <-- 修复！

        draw_list = []
        for point in trunk + tree + ground + stars + heart:
            x, y, z, base_color, is_light, phase = point

            if is_light:
                pulse = 0.55 + 0.45 * math.sin(t * 2.4 + phase)
                r = min(255, int(base_color[0] * pulse))
                g = min(255, int(base_color[1] * pulse))
                b = min(255, int(base_color[2] * pulse))
                color = (r, g, b)
            else:
                color = tuple(base_color)

            proj = project_point(x, y, z, rot_angle, zoom)
            if proj:
                sx, sy, depth = proj
                size = max(3, int((4.5 - depth * 0.13) * (0.7 + 0.3 * zoom)))
                draw_list.append((depth, sx, sy, size, color))

        draw_list.sort(key=lambda v: v[0], reverse=True)
        for _, sx, sy, size, color in draw_list:
            if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
                pygame.draw.circle(screen, color, (sx, sy), size)

        text1 = font_big.render("Merry Christmas", True, (255, 255, 255))
        text2 = font_small.render(
            "Auto-rotate: ON" if auto_rotate else "Auto-rotate: OFF",
            True,
            (210, 220, 255)
        )
        screen.blit(text1, (40, 40))
        screen.blit(text2, (44, 100))

        draw_snow2d(snow_surface, snow2d)
        screen.blit(snow_surface, (0, 0))

        pygame.display.flip()

    # pygame.quit()


if __name__ == "__main__":
    main()