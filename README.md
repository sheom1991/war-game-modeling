# War Game Simulation (background.png 기반)

## 개요
- background.png 이미지를 유일한 좌표계(칠판)로 사용
- 모든 유닛의 위치, 이동, 전투, 시각화는 background.png의 (x, y) 픽셀 좌표로만 처리

## 좌표계
- (0,0): background.png의 좌상단(왼쪽 위) 픽셀
- (width-1, height-1): 우하단(오른쪽 아래) 픽셀
- 모든 유닛 위치/이동/거리 계산은 이 픽셀 좌표계만 사용

## config.yaml 예시
```yaml
initial_positions:
  RED:
    TANK: [[100, 200], ...]
    ...
  BLUE:
    TANK: [[900, 200], ...]
    ...
```
- (x, y)는 background.png의 픽셀 좌표

## 실행법
1. background.png를 results/ 폴더에 준비
2. config.yaml에서 유닛 위치 등 설정
3. 실행: `python test_simulation.py`
4. 결과: results/with_drone/ 폴더에 mp4, png, json 등 생성

## 코드 구조
- background.png: 유일한 좌표계
- config.yaml: 유닛 위치 등 파라미터
- 모든 연산/시각화: (x, y) 픽셀 좌표만 사용

## 확장성
- terrain_mask.npy 등으로 지형 특성(고지, 수로 등) 추가 가능
- 유닛 상태(파괴, fire 등) 시각화/로그에 반영 가능

## TODO
- 유닛 상태별 시각화 개선 (fire, destroyed 등)
- 블루팀 이동/공격 로직 점검
- 지형 특성 반영 구조 추가