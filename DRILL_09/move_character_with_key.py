"""Drill #9: 방향키로 소년을 이동시키는 Pico2D 예제."""


from dataclasses import dataclass, field
from pathlib import Path
from math import hypot
from time import perf_counter

TUK_WIDTH, TUK_HEIGHT = 1280, 1024
MOVE_SPEED = 200.0
MAX_DELTA = 0.05
FRAME_INTERVAL = 0.1
FRAME_COUNT = 8
CELL_SIZE = 100
HALF_SIZE = CELL_SIZE / 2

ASSET_DIR = Path(__file__).resolve().parent


@dataclass
class Boy:
    x: float = TUK_WIDTH / 2
    y: float = TUK_HEIGHT / 2
    keys: set[str] = field(default_factory=set)
    frame: int = 0
    facing: str = 'right'
    moving: bool = False
    animation_time: float = 0.0

    def update(self, dt):
        dt = max(0.0, min(dt, MAX_DELTA))
        previous_state = (self.moving, self.facing)
        dx = int('right' in self.keys) - int('left' in self.keys)
        dy = int('up' in self.keys) - int('down' in self.keys)
        self.moving = bool(dx or dy)
        if dx:
            self.facing = 'right' if dx > 0 else 'left'
        length = hypot(dx, dy)
        if length:
            dx, dy = dx / length, dy / length
        self.x = max(HALF_SIZE, min(TUK_WIDTH - HALF_SIZE, self.x + dx * MOVE_SPEED * dt))
        self.y = max(HALF_SIZE, min(TUK_HEIGHT - HALF_SIZE, self.y + dy * MOVE_SPEED * dt))

        if previous_state != (self.moving, self.facing):
            self.frame = 0
            self.animation_time = 0.0
        else:
            self.animation_time += dt
            while self.animation_time + 1e-12 >= FRAME_INTERVAL:
                self.animation_time = max(0.0, self.animation_time - FRAME_INTERVAL)
                self.frame = (self.frame + 1) % FRAME_COUNT

    @property
    def sprite_row(self):
        # clip_draw는 이미지 아래를 기준으로 자를 행을 지정한다.
        return (0 if self.moving else 2) + int(self.facing == 'right')


def main():
    import pico2d as p2

    for filename in ('TUK_GROUND.png', 'animation_sheet.png'):
        path = ASSET_DIR / filename
        if not path.is_file():
            raise FileNotFoundError(f'필수 과제 이미지를 찾을 수 없습니다: {path}')

    p2.open_canvas(TUK_WIDTH, TUK_HEIGHT)
    try:
        tuk_ground = p2.load_image(str(ASSET_DIR / 'TUK_GROUND.png'))
        character = p2.load_image(str(ASSET_DIR / 'animation_sheet.png'))
        running = True
        boy = Boy()
        key_names = {
            p2.SDLK_RIGHT: 'right', p2.SDLK_LEFT: 'left',
            p2.SDLK_UP: 'up', p2.SDLK_DOWN: 'down',
        }

        def handle_events():
            nonlocal running
            for event in p2.get_events():
                if event.type == p2.SDL_QUIT:
                    running = False
                elif event.type == p2.SDL_KEYDOWN:
                    if event.key == p2.SDLK_ESCAPE:
                        running = False
                    elif event.key in key_names:
                        boy.keys.add(key_names[event.key])
                elif event.type == p2.SDL_KEYUP and event.key in key_names:
                    boy.keys.discard(key_names[event.key])

        previous_time = perf_counter()
        while running:
            handle_events()
            if not running:
                break
            current_time = perf_counter()
            if not p2.SDL_GetKeyboardFocus():
                boy.keys.clear()
            boy.update(current_time - previous_time)
            previous_time = current_time
            p2.clear_canvas()
            tuk_ground.draw(TUK_WIDTH // 2, TUK_HEIGHT // 2)
            character.clip_draw(
                boy.frame * CELL_SIZE, boy.sprite_row * CELL_SIZE,
                CELL_SIZE, CELL_SIZE, boy.x, boy.y,
            )
            p2.update_canvas()
            p2.delay(0.005)
    finally:
        p2.close_canvas()


if __name__ == '__main__':
    main()
