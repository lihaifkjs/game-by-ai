import math
import random
import pygame

# ================== 全局参数 ==================
WIDTH, HEIGHT = 1600, 900
BLACK = (0, 0, 0)

TREE_POINTS   = 50000
GROUND_POINTS = 4000
STAR_POINTS   = 1200
HEART_POINTS  = 1000
SNOW2D_POINTS = 12

CAM_DIST   = 13.0
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


# ================== 生成圣诞树点云 ==================
def gen_tree_points():
    pts = []
    loops = 9
    spiral_n = int(TREE_POINTS * 0.7)

    for _ in range(spiral_n):
        u = random.random()
        h = u ** 1.6
        y = TREE_HEIGHT * h + 0.2

        base_r = (1 - h) ** 1.1 * 3.2
        branch_wave = max(0.0, math.sin((h * 5.8 + 0.15) * math.tau))
        branch_factor = 1.0 + 0.65 * branch_wave
        base_r *= branch_factor

        t = u * loops * math.tau
        angle = t + random.uniform(-0.22, 0.22)
        r = base_r * random.uniform(0.85, 1.08)

        x = math.cos(angle) * r
        z = math.sin(angle) * r

        mid_boost = 1.0 - abs(h - 0.55) * 1.5
        mid_boost = max(0.15, mid_boost)

        # 浅蓝色基础色：降低红，提高蓝和少量绿
        base_r = 130 + int(50 * mid_boost)
        base_g = 200 + int(40 * mid_boost)
        base_b = 255

        color = [
            min(255, base_r + random.randint(-10, 15)),
            min(255, base_g + random.randint(-10, 20)),
            base_b,
        ]

        is_light = 1 if random.random() < 0.08 else 0
        light_phase = random.uniform(0, math.tau)

        if is_light:
            # 白色高光
            color = [255, 255, 255]

        pts.append([x, y, z, color, is_light, light_phase])

    fill_n = TREE_POINTS - spiral_n
    for _ in range(fill_n):
        h = random.random() ** 1.9
        y = TREE_HEIGHT * h + 0.2 + random.uniform(-0.08, 0.08)

        base_r = (1 - h) ** 1.1 * 4.3
        branch_wave = max(0.0, math.sin((h * 5.8 + 0.15) * math.tau))
        branch_factor = 1.0 + 0.65 * branch_wave
        base_r *= branch_factor

        r = base_r * math.sqrt(random.random())
        angle = random.random() * math.tau

        x = math.cos(angle) * r + random.uniform(-0.08, 0.08)
        z = math.sin(angle) * r + random.uniform(-0.08, 0.08)

        # 浅蓝色主体
        r0 = random.randint(140, 180)
        g0 = random.randint(210, 240)
        b0 = 255
        color = [r0, g0, b0]

        is_light = 1 if random.random() < 0.06 else 0
        light_phase = random.uniform(0, math.tau)

        if is_light:
            color = [255, 255, 255]

        pts.append([x, y, z, color, is_light, light_phase])

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
    top_y = TREE_HEIGHT + 0.05

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

            # 爱心也改为浅蓝白
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

    tree = gen_tree_points()
    ground = gen_ground_points()
    stars = gen_star_points()
    heart = gen_heart_points()
    snow2d = init_snow2d()
    snow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

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
        update_snow2d(snow2d, dt)

        draw_list = []
        for point in tree + ground + stars + heart:
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
                size = max(1, int((3.6 - depth * 0.13) * (0.7 + 0.3 * zoom)))
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