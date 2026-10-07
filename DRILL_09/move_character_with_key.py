"""Drill #9: 방향키로 소년을 이동시키는 Pico2D 예제."""


from pathlib import Path

TUK_WIDTH, TUK_HEIGHT = 1280, 1024

ASSET_DIR = Path(__file__).resolve().parent


def main():
    import pico2d as p2

    p2.open_canvas(TUK_WIDTH, TUK_HEIGHT)
    tuk_ground = p2.load_image(str(ASSET_DIR / 'TUK_GROUND.png'))
    character = p2.load_image(str(ASSET_DIR / 'animation_sheet.png'))
    running = True
    x, y = TUK_WIDTH // 2, TUK_HEIGHT // 2
    frame = 0

    def handle_events():
        nonlocal running, x
        for event in p2.get_events():
            if event.type == p2.SDL_QUIT:
                running = False
            elif event.type == p2.SDL_KEYDOWN:
                if event.key == p2.SDLK_RIGHT:
                    x += 10
                elif event.key == p2.SDLK_LEFT:
                    x -= 10
                elif event.key == p2.SDLK_ESCAPE:
                    running = False

    while running:
        handle_events()
        p2.clear_canvas()
        tuk_ground.draw(TUK_WIDTH // 2, TUK_HEIGHT // 2)
        character.clip_draw(frame * 100, 100, 100, 100, x, y)
        p2.update_canvas()
        frame = (frame + 1) % 8
        p2.delay(0.05)
    p2.close_canvas()


if __name__ == '__main__':
    main()
