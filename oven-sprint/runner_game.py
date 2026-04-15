import random
import tkinter as tk


# 화면 크기와 바닥 높이를 먼저 상수로 정해 둡니다.
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540
GROUND_Y = 430


class RunnerGame:
    def __init__(self, root):
        # tkinter 창의 기본 설정을 합니다.
        self.root = root
        self.root.title("점프 러너")
        self.root.resizable(False, False)

        # Canvas는 게임 화면을 직접 그리는 공간입니다.
        self.canvas = tk.Canvas(
            root,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bg="#f7f4ea",
            highlightthickness=0,
        )
        self.canvas.pack()

        # 키 입력을 받기 위해 점프 키를 연결합니다.
        self.root.bind("<space>", self.jump)
        self.root.bind("<Up>", self.jump)
        self.root.bind("<Return>", self.restart_game)
        self.root.bind("<Key-z>", self.slash)
        self.root.bind("<Key-Z>", self.slash)

        # 게임 루프에서 사용할 시간을 저장합니다.
        self.frame_ms = 16

        # 실제 게임 상태를 초기화합니다.
        self.reset_game()
        self.update_game()

    def reset_game(self):
        # 플레이어 위치와 속도를 시작값으로 되돌립니다.
        self.player_x = 180
        self.player_y = GROUND_Y
        self.player_width = 54
        self.player_height = 72
        self.player_velocity_y = 0
        self.gravity = 1.1
        self.jump_power = -18
        self.is_on_ground = True

        # 게임이 진행될수록 달리기 속도가 조금씩 빨라집니다.
        self.base_speed = 7.0
        self.game_speed = self.base_speed
        self.max_speed = 20.0
        self.speed_up = 0.0025

        # 장애물 목록과 생성 타이머를 준비합니다.
        self.obstacles = []
        self.spawn_timer = 0
        self.spawn_delay = 90

        # 코인도 별도의 목록과 생성 타이머로 관리합니다.
        self.coins = []
        self.coin_timer = 0
        self.coin_delay = 55
        self.coin_count = 0
        self.total_coins = 0
        self.bamboo_cuts = 0
        self.slash_effect_timer = 0
        self.particles = []

        # 점수와 생존 시간을 관리합니다.
        self.score = 0
        self.elapsed_frames = 0
        self.game_over = False

        # 바닥 줄무늬가 왼쪽으로 흐르는 효과를 위해 저장합니다.
        self.ground_offset = 0

    def jump(self, event=None):
        # 바닥 위에 있을 때만 점프하게 하면 조작이 단순해집니다.
        if self.game_over:
            return

        if self.is_on_ground:
            self.player_velocity_y = self.jump_power
            self.is_on_ground = False

    def restart_game(self, event=None):
        # 게임 오버 상태에서 엔터 키를 누르면 다시 시작합니다.
        if self.game_over:
            self.reset_game()

    def create_obstacle(self):
        # 장애물은 딕셔너리 하나로 표현합니다.
        # 초보자에게는 클래스를 여러 개 만드는 것보다 읽기 쉽습니다.
        width = random.randint(28, 46)
        height = random.randint(70, 135)
        obstacle = {
            "x": WINDOW_WIDTH + width,
            "y": GROUND_Y - height,
            "width": width,
            "height": height,
        }
        self.obstacles.append(obstacle)

    def create_coin_group(self):
        # 코인은 기본적으로 직선으로 배치하고,
        # 대나무와 겹치는 구간에서만 아치형으로 바꿉니다.
        coin_total = random.randint(5, 9)
        start_x = WINDOW_WIDTH + 40

        # 1cm 정도 간격으로 촘촘하게 보이도록 대략 38px 간격을 사용합니다.
        coin_spacing = 38

        # 플레이어가 편하게 먹는 기본 직선 높이입니다.
        straight_y = random.choice([GROUND_Y - 28, GROUND_Y - 42])
        arc_height = random.choice([52, 74, 96])
        end_x = start_x + (coin_total - 1) * coin_spacing

        # 코인 줄과 대나무가 겹칠 때만 아치형으로 들어 올립니다.
        use_arc = False
        for obstacle in self.obstacles:
            obstacle_left = obstacle["x"] - 12
            obstacle_right = obstacle["x"] + obstacle["width"] + 12
            overlap_x = end_x >= obstacle_left and start_x <= obstacle_right
            if overlap_x:
                use_arc = True
                break

        for index in range(coin_total):
            coin_y = straight_y
            if use_arc:
                distance_from_center = abs(index - (coin_total - 1) / 2)
                curve_ratio = 1 - (distance_from_center / max(1, coin_total / 2))
                coin_y = straight_y - curve_ratio * arc_height

            coin = {
                "x": start_x + index * coin_spacing,
                "y": coin_y,
                "radius": 14,
            }
            self.coins.append(coin)

    def update_player(self):
        # 중력 때문에 위로 올라간 뒤 다시 내려오게 됩니다.
        self.player_velocity_y += self.gravity
        self.player_y += self.player_velocity_y

        # 바닥보다 아래로 내려가면 바닥 위에 다시 고정합니다.
        if self.player_y >= GROUND_Y:
            self.player_y = GROUND_Y
            self.player_velocity_y = 0
            self.is_on_ground = True

    def update_obstacles(self):
        # 모든 장애물을 현재 속도만큼 왼쪽으로 이동시킵니다.
        for obstacle in self.obstacles:
            obstacle["x"] -= self.game_speed

        # 화면 밖으로 완전히 나간 장애물은 지워서 목록을 가볍게 유지합니다.
        self.obstacles = [
            obstacle
            for obstacle in self.obstacles
            if obstacle["x"] + obstacle["width"] > 0
        ]

        # 시간이 지날수록 약간 더 빨리, 약간 더 자주 장애물이 나옵니다.
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay:
            self.create_obstacle()
            self.spawn_timer = 0
            self.spawn_delay = random.randint(45, 95)

    def update_coins(self):
        # 코인도 장애물처럼 왼쪽으로 이동합니다.
        for coin in self.coins:
            coin["x"] -= self.game_speed

        self.coins = [
            coin
            for coin in self.coins
            if coin["x"] + coin["radius"] > 0
        ]

        # 코인은 장애물보다 조금 더 자주 나오게 합니다.
        self.coin_timer += 1
        if self.coin_timer >= self.coin_delay:
            self.create_coin_group()
            self.coin_timer = 0
            self.coin_delay = random.randint(40, 85)

    def slash(self, event=None):
        # Z 키를 누르면 베기 횟수를 1회 써서 대나무 하나를 벱니다.
        if self.game_over or self.bamboo_cuts <= 0:
            return

        for obstacle in list(self.obstacles):
            obstacle_left = obstacle["x"]
            obstacle_right = obstacle["x"] + obstacle["width"]
            in_slash_range = (
                obstacle_left < self.player_x + self.player_width + 95
                and obstacle_right > self.player_x + 8
            )

            if in_slash_range:
                self.obstacles.remove(obstacle)
                self.bamboo_cuts -= 1
                self.slash_effect_timer = 10
                self.score += 40
                self.spawn_bamboo_particles(obstacle)
                return

    def spawn_bamboo_particles(self, obstacle):
        # 베었을 때 대나무 조각이 흩어지도록 작은 파편을 만듭니다.
        center_x = obstacle["x"] + obstacle["width"] / 2
        center_y = obstacle["y"] + obstacle["height"] / 2

        for _ in range(12):
            particle = {
                "x": center_x,
                "y": center_y,
                "vx": random.uniform(-5.0, 6.5),
                "vy": random.uniform(-8.0, -1.5),
                "size": random.randint(4, 9),
                "life": random.randint(14, 22),
                "color": random.choice(["#7fb069", "#a7c957", "#5f8f48"]),
            }
            self.particles.append(particle)

    def update_particles(self):
        # 파편은 잠깐 날아가다가 사라집니다.
        remaining_particles = []

        for particle in self.particles:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["vy"] += 0.55
            particle["life"] -= 1

            if particle["life"] > 0:
                remaining_particles.append(particle)

        self.particles = remaining_particles

    def check_collision(self):
        # 충돌 판정은 보이는 대나무 줄기 위치에 더 가깝게 계산합니다.
        player_left = self.player_x
        player_top = self.player_y - self.player_height
        player_right = self.player_x + self.player_width
        player_bottom = self.player_y

        for obstacle in self.obstacles:
            stem_count = 3
            stem_width = obstacle["width"] / stem_count

            for index in range(stem_count):
                stem_x1 = obstacle["x"] + index * stem_width
                stem_x2 = stem_x1 + stem_width

                # 실제 판정은 줄기 가운데 부분만 사용해서 더 정확하게 맞춥니다.
                hit_left = stem_x1 + 4
                hit_right = stem_x2 - 4
                hit_top = obstacle["y"] + 6
                hit_bottom = obstacle["y"] + obstacle["height"]

                overlap_x = player_right > hit_left and player_left < hit_right
                overlap_y = player_bottom > hit_top and player_top < hit_bottom

                if overlap_x and overlap_y:
                    self.game_over = True
                    return

    def collect_coins(self):
        # 플레이어와 코인이 겹치면 코인을 먹습니다.
        player_left = self.player_x
        player_top = self.player_y - self.player_height
        player_right = self.player_x + self.player_width
        player_bottom = self.player_y

        remaining_coins = []

        for coin in self.coins:
            coin_left = coin["x"] - coin["radius"]
            coin_top = coin["y"] - coin["radius"]
            coin_right = coin["x"] + coin["radius"]
            coin_bottom = coin["y"] + coin["radius"]

            overlap_x = player_right > coin_left and player_left < coin_right
            overlap_y = player_bottom > coin_top and player_top < coin_bottom

            if overlap_x and overlap_y:
                self.coin_count += 1
                self.total_coins += 1
                if self.total_coins % 10 == 0:
                    self.bamboo_cuts += 1
                self.score += 25
            else:
                remaining_coins.append(coin)

        self.coins = remaining_coins

    def update_score(self):
        # 점수는 생존 시간과 현재 속도를 합쳐서 계산합니다.
        self.elapsed_frames += 1
        self.score += int(self.game_speed * 0.6)

        # 너무 빨라져서 플레이가 불가능해지지 않도록 최고 속도를 둡니다.
        self.game_speed = min(self.max_speed, self.game_speed + self.speed_up)
        self.ground_offset = (self.ground_offset + self.game_speed) % 80

    def draw_background(self):
        # 매 프레임마다 화면을 새로 그리기 때문에 먼저 전체를 지웁니다.
        self.canvas.delete("all")

        # 밤하늘 느낌이 나도록 어두운 색을 여러 겹으로 깔아 줍니다.
        self.canvas.create_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, fill="#0d1b2a", outline="")
        self.canvas.create_rectangle(0, 0, WINDOW_WIDTH, 220, fill="#132238", outline="")
        self.canvas.create_oval(690, 45, 835, 190, fill="#f1f5f9", outline="")
        self.canvas.create_oval(730, 45, 870, 180, fill="#132238", outline="")

        # 멀리 있는 산과 안개를 그려서 밤 배경을 만듭니다.
        self.canvas.create_polygon(
            0, 290, 120, 170, 240, 300, 360, 160, 520, 300, 680, 150, 860, 300, 960, 220, 960, 540, 0, 540,
            fill="#1b263b",
            outline="",
        )
        self.canvas.create_polygon(
            0, 340, 180, 230, 360, 350, 520, 240, 700, 340, 860, 250, 960, 330, 960, 540, 0, 540,
            fill="#243b55",
            outline="",
        )
        self.canvas.create_rectangle(0, 320, WINDOW_WIDTH, 390, fill="#31435c", outline="")

        # 대나무 숲은 반복문으로 여러 줄기를 배치하면 간단하게 표현할 수 있습니다.
        for x in range(-20, WINDOW_WIDTH + 80, 78):
            stem_top = 130 + (x % 5) * 12
            stem_color = "#355e3b" if (x // 78) % 2 == 0 else "#2f5233"
            self.canvas.create_rectangle(x, stem_top, x + 20, GROUND_Y + 25, fill=stem_color, outline="")

            for segment_y in range(stem_top + 28, GROUND_Y, 42):
                self.canvas.create_line(x, segment_y, x + 20, segment_y, fill="#1f3522", width=2)

            self.canvas.create_polygon(
                x + 10, stem_top + 50,
                x - 28, stem_top + 25,
                x - 6, stem_top + 62,
                fill="#5f8f48",
                outline="",
            )
            self.canvas.create_polygon(
                x + 10, stem_top + 86,
                x + 46, stem_top + 55,
                x + 18, stem_top + 102,
                fill="#7fb069",
                outline="",
            )

        self.canvas.create_rectangle(0, GROUND_Y, WINDOW_WIDTH, WINDOW_HEIGHT, fill="#3d5a40", outline="")
        self.canvas.create_rectangle(0, GROUND_Y - 10, WINDOW_WIDTH, GROUND_Y, fill="#588157", outline="")

        # 길 바닥 줄무늬를 움직이면 앞으로 달리는 느낌이 더 잘 납니다.
        stripe_x = -self.ground_offset
        while stripe_x < WINDOW_WIDTH:
            self.canvas.create_rectangle(
                stripe_x,
                GROUND_Y + 24,
                stripe_x + 52,
                GROUND_Y + 52,
                fill="#6b4f2a",
                outline="",
            )
            stripe_x += 80

        for stone_x in range(0, WINDOW_WIDTH, 95):
            offset = (stone_x * 3) % 18
            self.canvas.create_oval(
                stone_x - self.ground_offset * 0.2 % 95,
                GROUND_Y + 54 + offset,
                stone_x + 26 - self.ground_offset * 0.2 % 95,
                GROUND_Y + 66 + offset,
                fill="#a68a64",
                outline="",
            )

    def draw_player(self):
        # 플레이어를 오리지널 애니풍 검객 느낌으로 단순화해서 그립니다.
        x1 = self.player_x
        y1 = self.player_y - self.player_height
        x2 = self.player_x + self.player_width
        y2 = self.player_y

        # 머리와 머리카락입니다.
        self.canvas.create_oval(x1 + 8, y1 - 12, x2 - 8, y1 + 28, fill="#f6d7b0", outline="")
        self.canvas.create_arc(
            x1 + 4,
            y1 - 20,
            x2,
            y1 + 28,
            start=0,
            extent=180,
            fill="#1b1b1b",
            outline="",
        )
        self.canvas.create_polygon(
            x1 + 18, y1 + 2,
            x1 + 4, y1 + 28,
            x1 + 18, y1 + 24,
            fill="#1b1b1b",
            outline="",
        )
        self.canvas.create_polygon(
            x2 - 18, y1 + 2,
            x2 + 8, y1 + 18,
            x2 - 10, y1 + 26,
            fill="#1b1b1b",
            outline="",
        )

        # 얼굴 표정입니다.
        self.canvas.create_oval(x1 + 16, y1 + 2, x1 + 22, y1 + 8, fill="#2d3436", outline="")
        self.canvas.create_oval(x2 - 22, y1 + 2, x2 - 16, y1 + 8, fill="#2d3436", outline="")
        self.canvas.create_line(x1 + 18, y1 + 16, x2 - 18, y1 + 16, fill="#9b6a4f", width=2)

        # 옷은 단순한 검객 복장 느낌으로만 표현합니다.
        self.canvas.create_rectangle(x1 + 8, y1 + 26, x2 - 8, y2 - 6, fill="#1d3557", outline="")
        self.canvas.create_line(x1 + 27, y1 + 26, x1 + 27, y2 - 6, fill="#e9ecef", width=2)
        self.canvas.create_rectangle(x1 + 18, y1 + 44, x2 - 18, y1 + 50, fill="#c1121f", outline="")

        # 검은 허리 옆에 보이도록 그립니다.
        self.canvas.create_line(x2 - 2, y1 + 38, x2 + 22, y2 - 8, fill="#3a3a3a", width=5)
        self.canvas.create_line(x2 + 3, y1 + 42, x2 + 26, y2 - 6, fill="#d9d9d9", width=2)

        # 다리는 달리는 느낌이 나도록 약간 비대칭으로 그립니다.
        self.canvas.create_line(x1 + 20, y2 - 8, x1 + 12, y2 + 18, fill="#2d3436", width=5)
        self.canvas.create_line(x2 - 20, y2 - 8, x2 - 8, y2 + 14, fill="#2d3436", width=5)
        self.canvas.create_line(x1 + 10, y2 + 18, x1 + 26, y2 + 18, fill="#111111", width=4)
        self.canvas.create_line(x2 - 10, y2 + 14, x2 + 6, y2 + 14, fill="#111111", width=4)

        # 대나무를 벨 수 있을 때는 검 앞에 간단한 빛 효과를 보여 줍니다.
        if self.bamboo_cuts > 0:
            self.canvas.create_line(x2 + 10, y1 + 36, x2 + 34, y1 + 18, fill="#9bf6ff", width=3)

        if self.slash_effect_timer > 0:
            self.canvas.create_line(x2 - 4, y1 + 20, x2 + 42, y1 - 8, fill="#ffffff", width=5)
            self.canvas.create_line(x2 + 2, y1 + 28, x2 + 48, y1, fill="#90e0ef", width=3)

    def draw_coins(self):
        # 코인은 눈에 잘 띄도록 금색 원으로 그립니다.
        for coin in self.coins:
            self.canvas.create_oval(
                coin["x"] - coin["radius"],
                coin["y"] - coin["radius"],
                coin["x"] + coin["radius"],
                coin["y"] + coin["radius"],
                fill="#f4d35e",
                outline="#c98c10",
                width=2,
            )
            self.canvas.create_text(
                coin["x"],
                coin["y"],
                text="O",
                font=("Malgun Gothic", 10, "bold"),
                fill="#7a5200",
            )

    def draw_particles(self):
        # 흩어지는 대나무 조각을 작은 사각형으로 그립니다.
        for particle in self.particles:
            size = particle["size"]
            self.canvas.create_rectangle(
                particle["x"] - size / 2,
                particle["y"] - size / 2,
                particle["x"] + size / 2,
                particle["y"] + size / 2,
                fill=particle["color"],
                outline="",
            )

    def draw_obstacles(self):
        # 장애물은 대나무 다발처럼 보이도록 여러 줄기를 겹쳐 그립니다.
        for obstacle in self.obstacles:
            stem_count = 3
            stem_width = obstacle["width"] / stem_count

            for index in range(stem_count):
                stem_x1 = obstacle["x"] + index * stem_width
                stem_x2 = stem_x1 + stem_width - 4
                self.canvas.create_rectangle(
                    stem_x1,
                    obstacle["y"],
                    stem_x2,
                    obstacle["y"] + obstacle["height"],
                    fill="#7fb069",
                    outline="",
                )
                self.canvas.create_rectangle(
                    stem_x1 + 3,
                    obstacle["y"],
                    stem_x1 + 8,
                    obstacle["y"] + obstacle["height"],
                    fill="#a7c957",
                    outline="",
                )

                for segment_y in range(int(obstacle["y"] + 18), int(obstacle["y"] + obstacle["height"]), 28):
                    self.canvas.create_line(
                        stem_x1,
                        segment_y,
                        stem_x2,
                        segment_y,
                        fill="#386641",
                        width=2,
                    )

            self.canvas.create_polygon(
                obstacle["x"] + obstacle["width"] - 6,
                obstacle["y"] + 18,
                obstacle["x"] + obstacle["width"] + 26,
                obstacle["y"] + 2,
                obstacle["x"] + obstacle["width"] + 6,
                obstacle["y"] + 28,
                fill="#5f8f48",
                outline="",
            )

    def draw_hud(self):
        # 화면 위쪽에 점수와 조작 방법을 표시합니다.
        self.canvas.create_text(
            24,
            24,
            anchor="nw",
            text=f"점수 : {self.score}",
            font=("Malgun Gothic", 18, "bold"),
            fill="#1e272e",
        )
        self.canvas.create_text(
            24,
            56,
            anchor="nw",
            text=f"코인 : {self.coin_count}",
            font=("Malgun Gothic", 14),
            fill="#f4d35e",
        )
        self.canvas.create_text(
            24,
            84,
            anchor="nw",
            text=f"베기 : {self.bamboo_cuts}",
            font=("Malgun Gothic", 14),
            fill="#90e0ef",
        )
        self.canvas.create_text(
            24,
            112,
            anchor="nw",
            text=f"속도 : {self.game_speed:.1f}",
            font=("Malgun Gothic", 14),
            fill="#1e272e",
        )
        self.canvas.create_text(
            WINDOW_WIDTH / 2,
            28,
            text="스페이스/위쪽 화살표: 점프   Z: 베기",
            font=("Malgun Gothic", 14),
            fill="#2d3436",
        )

        if self.game_over:
            self.canvas.create_rectangle(
                180,
                140,
                780,
                370,
                fill="#ffffff",
                outline="#2d3436",
                width=3,
            )
            self.canvas.create_text(
                WINDOW_WIDTH / 2,
                200,
                text="게임 오버",
                font=("Malgun Gothic", 30, "bold"),
                fill="#d63031",
            )
            self.canvas.create_text(
                WINDOW_WIDTH / 2,
                250,
                text=f"최종 점수 : {self.score}",
                font=("Malgun Gothic", 20),
                fill="#2d3436",
            )
            self.canvas.create_text(
                WINDOW_WIDTH / 2,
                300,
                text="엔터 키를 누르면 다시 시작합니다.",
                font=("Malgun Gothic", 17),
                fill="#2d3436",
            )

    def update_game(self):
        # 게임 오버가 아니면 물리, 장애물, 점수를 계속 갱신합니다.
        if not self.game_over:
            self.update_player()
            self.update_obstacles()
            self.update_coins()
            self.check_collision()
            self.collect_coins()
            self.update_score()
            self.update_particles()

            if self.slash_effect_timer > 0:
                self.slash_effect_timer -= 1
        else:
            self.update_particles()

        # 마지막에는 항상 현재 상태를 화면에 다시 그립니다.
        self.draw_background()
        self.draw_player()
        self.draw_coins()
        self.draw_obstacles()
        self.draw_particles()
        self.draw_hud()

        # after 함수는 "몇 ms 뒤에 다시 이 함수를 실행"하라는 뜻입니다.
        self.root.after(self.frame_ms, self.update_game)


def main():
    # 프로그램 시작 지점입니다.
    root = tk.Tk()
    RunnerGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
