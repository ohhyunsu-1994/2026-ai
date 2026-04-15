const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const overlay = document.getElementById("overlay");
const startButton = document.getElementById("startButton");
const overlayCopy = document.getElementById("overlayCopy");
const scoreNode = document.getElementById("score");
const coinCountNode = document.getElementById("coinCount");
const slashCountNode = document.getElementById("slashCount");
const speedLabelNode = document.getElementById("speedLabel");

const DPR = Math.min(window.devicePixelRatio || 1, 2);
const WORLD = { width: 960, height: 540 };
const GROUND_Y = 430;

let lastTime = 0;
let gameStarted = false;
let touchStartY = null;

const state = {
  time: 0,
  speed: 7,
  score: 0,
  coinCount: 0,
  totalCoins: 0,
  bambooCuts: 0,
  spawnTimer: 0,
  spawnDelay: 1.2,
  coinTimer: 0,
  coinDelay: 0.8,
  groundOffset: 0,
  slashEffectTimer: 0,
  obstacles: [],
  coins: [],
  particles: [],
  player: null,
};

function resetGame() {
  state.time = 0;
  state.speed = 7;
  state.score = 0;
  state.coinCount = 0;
  state.totalCoins = 0;
  state.bambooCuts = 0;
  state.spawnTimer = 0;
  state.spawnDelay = 1.2;
  state.coinTimer = 0.35;
  state.coinDelay = 0.8;
  state.groundOffset = 0;
  state.slashEffectTimer = 0;
  state.obstacles = [];
  state.coins = [];
  state.particles = [];
  state.player = {
    x: 180,
    y: GROUND_Y,
    width: 54,
    height: 72,
    vy: 0,
    onGround: true,
  };
  updateHud();
}

function updateHud() {
  scoreNode.textContent = Math.floor(state.score).toString();
  coinCountNode.textContent = state.coinCount.toString();
  slashCountNode.textContent = state.bambooCuts.toString();
  speedLabelNode.textContent = `속도 ${state.speed.toFixed(1)}`;
}

function resizeCanvas() {
  const rect = canvas.getBoundingClientRect();
  canvas.width = Math.floor(rect.width * DPR);
  canvas.height = Math.floor(rect.height * DPR);
  ctx.setTransform(canvas.width / WORLD.width, 0, 0, canvas.height / WORLD.height, 0, 0);
}

function startGame() {
  resetGame();
  gameStarted = true;
  overlay.classList.add("hidden");
}

function endGame() {
  gameStarted = false;
  overlay.classList.remove("hidden");
  startButton.textContent = "다시 시작";
  overlayCopy.textContent =
    `점수 ${Math.floor(state.score)}점, 코인 ${state.coinCount}개를 모았습니다. 코인 10개마다 베기 1회를 얻고, Z 키로 직접 대나무를 베어보세요.`;
}

function jump() {
  if (!gameStarted) {
    startGame();
    return;
  }
  if (!state.player.onGround) return;
  state.player.vy = -18;
  state.player.onGround = false;
}

function slash() {
  if (!gameStarted || state.bambooCuts <= 0) return;

  for (let i = 0; i < state.obstacles.length; i += 1) {
    const obstacle = state.obstacles[i];
    const obstacleLeft = obstacle.x;
    const obstacleRight = obstacle.x + obstacle.width;
    const inRange = obstacleLeft < state.player.x + state.player.width + 95 &&
      obstacleRight > state.player.x + 8;

    if (inRange) {
      state.obstacles.splice(i, 1);
      state.bambooCuts -= 1;
      state.slashEffectTimer = 0.18;
      state.score += 40;
      spawnBambooParticles(obstacle);
      updateHud();
      return;
    }
  }
}

function createObstacle() {
  state.obstacles.push({
    x: WORLD.width + 40,
    y: GROUND_Y - (70 + Math.random() * 65),
    width: 28 + Math.random() * 18,
    height: 70 + Math.random() * 65,
  });
}

function createCoinGroup() {
  const coinTotal = 5 + Math.floor(Math.random() * 5);
  const startX = WORLD.width + 40;
  const coinSpacing = 38;
  const straightY = Math.random() > 0.5 ? GROUND_Y - 28 : GROUND_Y - 42;
  const arcHeightOptions = [52, 74, 96];
  const arcHeight = arcHeightOptions[Math.floor(Math.random() * arcHeightOptions.length)];
  const endX = startX + (coinTotal - 1) * coinSpacing;

  let useArc = false;
  for (const obstacle of state.obstacles) {
    const obstacleLeft = obstacle.x - 12;
    const obstacleRight = obstacle.x + obstacle.width + 12;
    if (endX >= obstacleLeft && startX <= obstacleRight) {
      useArc = true;
      break;
    }
  }

  for (let index = 0; index < coinTotal; index += 1) {
    let coinY = straightY;
    if (useArc) {
      const centerDistance = Math.abs(index - (coinTotal - 1) / 2);
      const curveRatio = 1 - (centerDistance / Math.max(1, coinTotal / 2));
      coinY = straightY - curveRatio * arcHeight;
    }

    state.coins.push({
      x: startX + index * coinSpacing,
      y: coinY,
      radius: 14,
    });
  }
}

function playerBounds() {
  return {
    left: state.player.x,
    top: state.player.y - state.player.height,
    right: state.player.x + state.player.width,
    bottom: state.player.y,
  };
}

function overlaps(a, b) {
  return a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top;
}

function spawnBambooParticles(obstacle) {
  const centerX = obstacle.x + obstacle.width / 2;
  const centerY = obstacle.y + obstacle.height / 2;

  for (let i = 0; i < 12; i += 1) {
    state.particles.push({
      x: centerX,
      y: centerY,
      vx: -160 + Math.random() * 360,
      vy: -280 + Math.random() * 200,
      size: 4 + Math.random() * 6,
      life: 0.35 + Math.random() * 0.22,
      color: ["#7fb069", "#a7c957", "#5f8f48"][Math.floor(Math.random() * 3)],
    });
  }
}

function updatePlayer(dt) {
  state.player.vy += 1.1 * 60 * dt;
  state.player.y += state.player.vy * 60 * dt;

  if (state.player.y >= GROUND_Y) {
    state.player.y = GROUND_Y;
    state.player.vy = 0;
    state.player.onGround = true;
  }
}

function updateObstacles(dt) {
  const speedPx = state.speed * 60;
  state.obstacles = state.obstacles.filter((obstacle) => {
    obstacle.x -= speedPx * dt;
    return obstacle.x + obstacle.width > -20;
  });

  state.spawnTimer -= dt;
  if (state.spawnTimer <= 0) {
    createObstacle();
    state.spawnTimer = 0.75 + Math.random() * 0.7;
  }
}

function updateCoins(dt) {
  const speedPx = state.speed * 60;
  state.coins = state.coins.filter((coin) => {
    coin.x -= speedPx * dt;
    return coin.x + coin.radius > -20;
  });

  state.coinTimer -= dt;
  if (state.coinTimer <= 0) {
    createCoinGroup();
    state.coinTimer = 0.55 + Math.random() * 0.55;
  }
}

function collectCoins() {
  const player = playerBounds();
  state.coins = state.coins.filter((coin) => {
    const coinBox = {
      left: coin.x - coin.radius,
      top: coin.y - coin.radius,
      right: coin.x + coin.radius,
      bottom: coin.y + coin.radius,
    };

    if (overlaps(player, coinBox)) {
      state.coinCount += 1;
      state.totalCoins += 1;
      state.score += 25;
      if (state.totalCoins % 10 === 0) state.bambooCuts += 1;
      return false;
    }
    return true;
  });
}

function checkObstacleHit() {
  const player = playerBounds();
  for (const obstacle of state.obstacles) {
    const stemCount = 3;
    const stemWidth = obstacle.width / stemCount;

    for (let i = 0; i < stemCount; i += 1) {
      const stemX1 = obstacle.x + i * stemWidth;
      const stemX2 = stemX1 + stemWidth;
      const hitBox = {
        left: stemX1 + 4,
        top: obstacle.y + 6,
        right: stemX2 - 4,
        bottom: obstacle.y + obstacle.height,
      };

      if (overlaps(player, hitBox)) {
        endGame();
        return;
      }
    }
  }
}

function updateParticles(dt) {
  state.particles = state.particles.filter((particle) => {
    particle.life -= dt;
    particle.x += particle.vx * dt;
    particle.y += particle.vy * dt;
    particle.vy += 650 * dt;
    return particle.life > 0;
  });
}

function update(dt) {
  if (!gameStarted) {
    updateParticles(dt);
    return;
  }

  state.time += dt;
  state.speed = Math.min(20, state.speed + 0.0025 * 60 * dt);
  state.score += state.speed * 36 * dt;
  state.groundOffset = (state.groundOffset + state.speed * 60 * dt) % 95;

  updatePlayer(dt);
  updateObstacles(dt);
  updateCoins(dt);
  collectCoins();
  checkObstacleHit();
  updateParticles(dt);

  if (state.slashEffectTimer > 0) {
    state.slashEffectTimer = Math.max(0, state.slashEffectTimer - dt);
  }

  updateHud();
}

function drawBackground() {
  ctx.fillStyle = "#0d1b2a";
  ctx.fillRect(0, 0, WORLD.width, WORLD.height);
  ctx.fillStyle = "#132238";
  ctx.fillRect(0, 0, WORLD.width, 220);

  ctx.fillStyle = "#f1f5f9";
  ctx.beginPath();
  ctx.arc(760, 118, 72, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#132238";
  ctx.beginPath();
  ctx.arc(792, 110, 68, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = "#1b263b";
  ctx.beginPath();
  ctx.moveTo(0, 290);
  ctx.lineTo(120, 170);
  ctx.lineTo(240, 300);
  ctx.lineTo(360, 160);
  ctx.lineTo(520, 300);
  ctx.lineTo(680, 150);
  ctx.lineTo(860, 300);
  ctx.lineTo(960, 220);
  ctx.lineTo(960, 540);
  ctx.lineTo(0, 540);
  ctx.closePath();
  ctx.fill();

  ctx.fillStyle = "#243b55";
  ctx.beginPath();
  ctx.moveTo(0, 340);
  ctx.lineTo(180, 230);
  ctx.lineTo(360, 350);
  ctx.lineTo(520, 240);
  ctx.lineTo(700, 340);
  ctx.lineTo(860, 250);
  ctx.lineTo(960, 330);
  ctx.lineTo(960, 540);
  ctx.lineTo(0, 540);
  ctx.closePath();
  ctx.fill();

  ctx.fillStyle = "#31435c";
  ctx.fillRect(0, 320, WORLD.width, 70);

  for (let x = -20; x < WORLD.width + 80; x += 78) {
    const stemTop = 130 + (x % 5) * 12;
    ctx.fillStyle = Math.floor(x / 78) % 2 === 0 ? "#355e3b" : "#2f5233";
    ctx.fillRect(x, stemTop, 20, GROUND_Y + 25 - stemTop);

    ctx.strokeStyle = "#1f3522";
    ctx.lineWidth = 2;
    for (let y = stemTop + 28; y < GROUND_Y; y += 42) {
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(x + 20, y);
      ctx.stroke();
    }

    ctx.fillStyle = "#5f8f48";
    ctx.beginPath();
    ctx.moveTo(x + 10, stemTop + 50);
    ctx.lineTo(x - 28, stemTop + 25);
    ctx.lineTo(x - 6, stemTop + 62);
    ctx.closePath();
    ctx.fill();

    ctx.fillStyle = "#7fb069";
    ctx.beginPath();
    ctx.moveTo(x + 10, stemTop + 86);
    ctx.lineTo(x + 46, stemTop + 55);
    ctx.lineTo(x + 18, stemTop + 102);
    ctx.closePath();
    ctx.fill();
  }

  ctx.fillStyle = "#3d5a40";
  ctx.fillRect(0, GROUND_Y, WORLD.width, WORLD.height - GROUND_Y);
  ctx.fillStyle = "#588157";
  ctx.fillRect(0, GROUND_Y - 10, WORLD.width, 10);

  for (let stripeX = -state.groundOffset; stripeX < WORLD.width + 80; stripeX += 95) {
    ctx.fillStyle = "#6b4f2a";
    ctx.fillRect(stripeX, GROUND_Y + 24, 52, 28);
  }

  for (let stoneX = 0; stoneX < WORLD.width; stoneX += 95) {
    const offset = (stoneX * 3) % 18;
    const drawX = stoneX - (state.groundOffset * 0.2 % 95);
    ctx.fillStyle = "#a68a64";
    ctx.beginPath();
    ctx.ellipse(drawX + 13, GROUND_Y + 60 + offset, 13, 6, 0, 0, Math.PI * 2);
    ctx.fill();
  }
}

function drawPlayer() {
  const x1 = state.player.x;
  const y1 = state.player.y - state.player.height;
  const x2 = state.player.x + state.player.width;
  const y2 = state.player.y;

  ctx.fillStyle = "#f6d7b0";
  ctx.beginPath();
  ctx.ellipse((x1 + x2) / 2, y1 + 8, 19, 20, 0, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = "#1b1b1b";
  ctx.beginPath();
  ctx.arc((x1 + x2) / 2, y1 + 4, 24, Math.PI, 0);
  ctx.lineTo(x2 - 8, y1 + 8);
  ctx.lineTo(x1 + 8, y1 + 8);
  ctx.closePath();
  ctx.fill();

  ctx.beginPath();
  ctx.moveTo(x1 + 18, y1 + 2);
  ctx.lineTo(x1 + 4, y1 + 28);
  ctx.lineTo(x1 + 18, y1 + 24);
  ctx.closePath();
  ctx.fill();

  ctx.beginPath();
  ctx.moveTo(x2 - 18, y1 + 2);
  ctx.lineTo(x2 + 8, y1 + 18);
  ctx.lineTo(x2 - 10, y1 + 26);
  ctx.closePath();
  ctx.fill();

  ctx.fillStyle = "#2d3436";
  ctx.beginPath();
  ctx.arc(x1 + 19, y1 + 6, 3, 0, Math.PI * 2);
  ctx.arc(x2 - 19, y1 + 6, 3, 0, Math.PI * 2);
  ctx.fill();

  ctx.strokeStyle = "#9b6a4f";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(x1 + 18, y1 + 16);
  ctx.lineTo(x2 - 18, y1 + 16);
  ctx.stroke();

  ctx.fillStyle = "#1d3557";
  ctx.fillRect(x1 + 8, y1 + 26, x2 - x1 - 16, y2 - y1 - 32);
  ctx.strokeStyle = "#e9ecef";
  ctx.beginPath();
  ctx.moveTo(x1 + 27, y1 + 26);
  ctx.lineTo(x1 + 27, y2 - 6);
  ctx.stroke();
  ctx.fillStyle = "#c1121f";
  ctx.fillRect(x1 + 18, y1 + 44, x2 - x1 - 36, 6);

  ctx.strokeStyle = "#3a3a3a";
  ctx.lineWidth = 5;
  ctx.beginPath();
  ctx.moveTo(x2 - 2, y1 + 38);
  ctx.lineTo(x2 + 22, y2 - 8);
  ctx.stroke();
  ctx.strokeStyle = "#d9d9d9";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(x2 + 3, y1 + 42);
  ctx.lineTo(x2 + 26, y2 - 6);
  ctx.stroke();

  ctx.strokeStyle = "#2d3436";
  ctx.lineWidth = 5;
  ctx.beginPath();
  ctx.moveTo(x1 + 20, y2 - 8);
  ctx.lineTo(x1 + 12, y2 + 18);
  ctx.moveTo(x2 - 20, y2 - 8);
  ctx.lineTo(x2 - 8, y2 + 14);
  ctx.stroke();

  ctx.strokeStyle = "#111111";
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.moveTo(x1 + 10, y2 + 18);
  ctx.lineTo(x1 + 26, y2 + 18);
  ctx.moveTo(x2 - 10, y2 + 14);
  ctx.lineTo(x2 + 6, y2 + 14);
  ctx.stroke();

  if (state.bambooCuts > 0) {
    ctx.strokeStyle = "#9bf6ff";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(x2 + 10, y1 + 36);
    ctx.lineTo(x2 + 34, y1 + 18);
    ctx.stroke();
  }

  if (state.slashEffectTimer > 0) {
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 5;
    ctx.beginPath();
    ctx.moveTo(x2 - 4, y1 + 20);
    ctx.lineTo(x2 + 42, y1 - 8);
    ctx.stroke();
    ctx.strokeStyle = "#90e0ef";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(x2 + 2, y1 + 28);
    ctx.lineTo(x2 + 48, y1);
    ctx.stroke();
  }
}

function drawCoins() {
  for (const coin of state.coins) {
    ctx.fillStyle = "#f4d35e";
    ctx.strokeStyle = "#c98c10";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(coin.x, coin.y, coin.radius, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#7a5200";
    ctx.font = 'bold 10px "Trebuchet MS"';
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("O", coin.x, coin.y + 1);
  }
}

function drawObstacles() {
  for (const obstacle of state.obstacles) {
    const stemCount = 3;
    const stemWidth = obstacle.width / stemCount;

    for (let i = 0; i < stemCount; i += 1) {
      const stemX1 = obstacle.x + i * stemWidth;
      const stemX2 = stemX1 + stemWidth - 4;

      ctx.fillStyle = "#7fb069";
      ctx.fillRect(stemX1, obstacle.y, stemX2 - stemX1, obstacle.height);
      ctx.fillStyle = "#a7c957";
      ctx.fillRect(stemX1 + 3, obstacle.y, 5, obstacle.height);

      ctx.strokeStyle = "#386641";
      ctx.lineWidth = 2;
      for (let segmentY = obstacle.y + 18; segmentY < obstacle.y + obstacle.height; segmentY += 28) {
        ctx.beginPath();
        ctx.moveTo(stemX1, segmentY);
        ctx.lineTo(stemX2, segmentY);
        ctx.stroke();
      }
    }

    ctx.fillStyle = "#5f8f48";
    ctx.beginPath();
    ctx.moveTo(obstacle.x + obstacle.width - 6, obstacle.y + 18);
    ctx.lineTo(obstacle.x + obstacle.width + 26, obstacle.y + 2);
    ctx.lineTo(obstacle.x + obstacle.width + 6, obstacle.y + 28);
    ctx.closePath();
    ctx.fill();
  }
}

function drawParticles() {
  for (const particle of state.particles) {
    ctx.globalAlpha = Math.max(0, particle.life * 2.2);
    ctx.fillStyle = particle.color;
    ctx.fillRect(
      particle.x - particle.size / 2,
      particle.y - particle.size / 2,
      particle.size,
      particle.size,
    );
  }
  ctx.globalAlpha = 1;
}

function draw() {
  drawBackground();
  drawPlayer();
  drawCoins();
  drawObstacles();
  drawParticles();
}

function frame(ts) {
  if (!lastTime) lastTime = ts;
  const dt = Math.min((ts - lastTime) / 1000, 0.033);
  lastTime = ts;
  update(dt);
  draw();
  requestAnimationFrame(frame);
}

function onPointerDown(event) {
  if (event.target === startButton) return;
  touchStartY = event.clientY;
}

function onPointerUp(event) {
  if (touchStartY === null) return;
  const deltaY = event.clientY - touchStartY;
  if (deltaY > 32) {
    slash();
  } else {
    jump();
  }
  touchStartY = null;
}

window.addEventListener("resize", resizeCanvas);
canvas.addEventListener("pointerdown", onPointerDown);
canvas.addEventListener("pointerup", onPointerUp);
canvas.addEventListener("pointercancel", () => {
  touchStartY = null;
});

window.addEventListener("keydown", (event) => {
  if (event.code === "Space" || event.code === "ArrowUp") {
    event.preventDefault();
    jump();
  } else if (event.code === "KeyZ") {
    slash();
  }
});

startButton.addEventListener("click", startGame);

resizeCanvas();
resetGame();
requestAnimationFrame(frame);
