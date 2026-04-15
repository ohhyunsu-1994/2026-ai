# Bamboo Moon Runner

밤의 대나무 숲을 달리는 웹 러닝게임입니다.

## 조작

- `Space` / `위 화살표` / 화면 탭: 점프
- `Z` / 아래로 스와이프: 베기

## 규칙

- 코인을 먹으면 점수가 올라갑니다.
- 코인 10개를 모을 때마다 베기 1회가 쌓입니다.
- 대나무가 길을 막으면 베기로 직접 잘라 지나갈 수 있습니다.
- 코인은 기본적으로 직선으로 나오고, 대나무와 겹치는 구간에서는 아치형으로 배치됩니다.

## 로컬 실행

Python이 설치되어 있다면 아래처럼 간단히 실행할 수 있습니다.

```powershell
cd C:\Users\dlrhd\Documents\oven-sprint
python -m http.server 8000
```

브라우저에서 아래 주소를 열면 됩니다.

```text
http://localhost:8000
```

## ngrok 공개

로컬 서버를 켠 뒤 아래 명령으로 외부 접속 주소를 열 수 있습니다.

```powershell
ngrok http 8000
```

## GitHub CLI 공개 저장소 업로드

`gh` 로그인이 끝난 뒤 아래 순서로 공개 저장소를 만들 수 있습니다.

```powershell
cd C:\Users\dlrhd\Documents\oven-sprint
git init
git add .
git commit -m "Initial web runner game"
gh repo create bamboo-moon-runner --public --source=. --remote=origin --push
```
