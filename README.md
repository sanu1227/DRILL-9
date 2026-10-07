# Drill #9 — 소년 상하좌우 이동

방향키로 소년을 이동시키는 Pico2D 과제입니다. 개발 기준은 [PRD.md](PRD.md)에 있습니다.

## 실행

Python과 Pico2D를 준비한 뒤 저장소 루트에서 실행합니다.

```powershell
python -m pip install -r requirements.txt
python DRILL_09/move_character_with_key.py
```

방향키로 이동하고 Escape로 종료합니다. 창 닫기 버튼으로도 종료할 수 있습니다.
기존 마우스 이동 및 자동 달리기 파일은 별도 수업 예제입니다.

## 제출

저장소 이름: `DRILL-9` (GitHub에서 공백 대신 하이픈 사용)

제출 URL: https://github.com/sanu1227/DRILL-9.git

## 검증

```powershell
python -m unittest discover -s tests -v
```

화면과 입력의 수동 검사 순서는 [실제 창 검증 절차](docs/manual-checks.md)에 있습니다.
