# 이 저장소에서 작업할 때 지킬 것

유민혁(minhyuk94)의 개인 프로젝트 "해솔국 이야기". 사용자는 한국어로 대화합니다. 게임 글자도 한국어.

## 무엇인가

2000년대 초 국산 온라인 RPG 감성의 2D 탑다운 RPG (지금은 혼자 하는 게임, 나중에 서버를 붙일 수 있게 구조를 나눔).
Godot 4(GDScript), 웹으로 내보내 GitHub Pages(`https://minhyuk94.github.io/haesol/`)에 올린다.

## 지킬 것

- 옛 온라인 RPG에서 영감을 받았지만 **새로 만든 세계관**이다. 다른 게임의 이름·캐릭터·그림·음악·지도·지명을 쓰지 않고, 다른 회사·게임 이름을 README·화면·이력서에 넣지 않는다.
- **그림·소리·지도는 코드로 만든다.** `tools/art/`(도트 그림, 캐릭터는 몸·옷·머리 층을 따로 그려 게임에서 합침), `tools/sound/`, `tools/maps/`(→ `data/maps.json`). 결과 파일을 직접 고치지 말고 생성기를 고친다. 글꼴만 예외(갈무리, OFL).
- 게임 규칙(능력치·피해·경험치·아이템·상점·퀘스트 판정)은 `scripts/core/`에 화면과 분리해 둔다 → 나중에 서버로 옮길 수 있게. 테스트는 `tests/run_tests.gd`.
- 데이터(직업·기술·몬스터·아이템·퀘스트·대사)는 `data/*.json`. 바꾸면 테스트가 서로 맞는지 확인한다.
- CI(`ci.yml`): 생성기 재실행 → 테스트 → 켜지는지 → 웹 내보내기 → Pages 배포.
- 큰 기능이 바뀌면 이력서 저장소(minhyuk94.github.io)의 `games` 카드도 ko/ja/en으로 맞춘다. 소스 코드·저장소 링크는 이력서에 넣지 않는다.

## 이 작업 환경에서 돌려 보기

- npm/pip 설치와 github.io 접속이 막혀 있을 수 있다. Godot 실행 파일·웹 템플릿·글꼴은 dalmaru 저장소의 `godot-bin` 브랜치에서 가져온다 (`/opt/godot`에 풀어 둠).
- 화면 확인: `xvfb-run godot --rendering-driver opengl3 --audio-driver Dummy -- --dev=<장면> --out=/tmp/x` (`scripts/dev.gd`)
- 웹 확인: `godot --headless --export-release "Web" build/web/index.html` 후 로컬 http 서버 + headless Chrome(swiftshader).
