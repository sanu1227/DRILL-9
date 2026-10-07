"""실행: python -m unittest discover -s tests -v (창을 열지 않음)."""

from math import hypot
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'DRILL_09'))
import move_character_with_key as app
from move_character_with_key import Boy, TUK_WIDTH, TUK_HEIGHT, HALF_SIZE


class Drill9Checks(unittest.TestCase):
    def test_direction_key_sequence(self):
        boy = Boy()
        start_x, start_y = boy.x, boy.y
        boy.keys.add('right')
        for _ in range(20):
            boy.update(0.05)
        self.assertAlmostEqual(boy.x, start_x + 200)
        self.assertEqual(boy.y, start_y)
        boy.keys.add('left')
        boy.update(0.05)
        self.assertFalse(boy.moving)
        self.assertEqual(boy.x, start_x + 200)
        boy.keys.discard('right')
        boy.update(0.05)
        self.assertEqual(boy.x, start_x + 190)
        self.assertEqual(boy.facing, 'left')
        boy.keys = {'up'}
        boy.update(0.05)
        self.assertEqual(boy.y, start_y + 10)
        self.assertEqual(boy.facing, 'left')
        boy.keys = {'down'}
        boy.update(0.05)
        self.assertEqual(boy.y, start_y)
        boy.keys.clear()
        boy.update(0.05)
        self.assertFalse(boy.moving)
        self.assertEqual(boy.x, start_x + 190)
        boy.keys = {'up', 'right'}
        x, y = boy.x, boy.y
        boy.update(0.05)
        self.assertAlmostEqual(hypot(boy.x - x, boy.y - y), 10)
        other = Boy(keys={'right'})
        for _ in range(100):
            other.update(0.01)
        self.assertAlmostEqual(other.x, start_x + 200)

    def test_idle_run_animation_lifecycle(self):
        boy = Boy()
        self.assertEqual(boy.sprite_row, 3)
        boy.update(0.05)
        self.assertEqual(boy.frame, 0)
        boy.update(0.05)
        self.assertEqual(boy.frame, 1)
        for _ in range(14):
            boy.update(0.05)
        self.assertEqual(boy.frame, 0)
        boy.keys.add('right')
        boy.update(0.05)
        self.assertEqual((boy.sprite_row, boy.frame), (1, 0))
        for _ in range(20):
            boy.keys.add('right')  # 반복 KEYDOWN은 집합을 변경하지 않는다.
            boy.update(0.01)
        self.assertEqual(boy.frame, 2)
        boy.keys = {'left'}
        boy.update(0.01)
        self.assertEqual((boy.sprite_row, boy.frame), (0, 0))
        boy.keys.clear()
        boy.update(0.01)
        self.assertEqual((boy.sprite_row, boy.frame), (2, 0))
        boy.keys = {'up'}
        boy.update(0.01)
        self.assertEqual(boy.sprite_row, 0)
        boy.keys = {'up', 'down'}
        boy.update(0.01)
        self.assertEqual(boy.sprite_row, 2)

    def test_boundaries_and_time_guards(self):
        for keys, expected in (
            ({'left', 'down'}, (HALF_SIZE, HALF_SIZE)),
            ({'left', 'up'}, (HALF_SIZE, TUK_HEIGHT - HALF_SIZE)),
            ({'right', 'down'}, (TUK_WIDTH - HALF_SIZE, HALF_SIZE)),
            ({'right', 'up'}, (TUK_WIDTH - HALF_SIZE, TUK_HEIGHT - HALF_SIZE)),
        ):
            with self.subTest(keys=keys):
                boy = Boy(keys=keys)
                for _ in range(200):
                    boy.update(0.05)
                self.assertEqual((boy.x, boy.y), expected)
                boy.update(0.05)
                self.assertEqual((boy.x, boy.y), expected)
                self.assertTrue(boy.moving)
                boy.keys.clear()
                boy.update(0.05)
                self.assertFalse(boy.moving)
        boy = Boy(keys={'right'})
        x = boy.x
        boy.update(100)
        self.assertEqual(boy.x, x + 10)
        boy.update(-1)
        self.assertEqual(boy.x, x + 10)

    def test_main_event_wiring_and_cleanup(self):
        # 가짜 화면은 입력 연결과 자원 정리만 검사한다. 실제 렌더링은 별도 확인한다.
        image = Mock()
        event = lambda kind, key=None: SimpleNamespace(type=kind, key=key)
        fake = SimpleNamespace(
            SDL_QUIT=0, SDL_KEYDOWN=1, SDL_KEYUP=2,
            SDLK_RIGHT=10, SDLK_LEFT=11, SDLK_UP=12, SDLK_DOWN=13, SDLK_ESCAPE=14,
            open_canvas=Mock(), close_canvas=Mock(), load_image=Mock(return_value=image),
            clear_canvas=Mock(), update_canvas=Mock(), delay=Mock(),
            SDL_GetKeyboardFocus=Mock(side_effect=[1, 1, 1, 1, 1, 0]),
            get_events=Mock(side_effect=[
                [event(1, 10)], [], [event(1, 12)], [event(2, 10)],
                [event(1, 11), event(2, 12)], [], [event(0)],
            ]),
        )
        with patch.dict(sys.modules, {'pico2d': fake}), patch.object(
            app, 'perf_counter', side_effect=[i / 100 for i in range(20)]
        ):
            app.main()
        draws = [call.args for call in image.clip_draw.call_args_list]
        self.assertEqual([draw[1] for draw in draws], [100, 100, 100, 100, 0, 200])
        self.assertEqual(draws[3][4], draws[2][4])  # 오른쪽 해제 후 위쪽만 이동.
        self.assertEqual(draws[5][4:], draws[4][4:])  # 포커스 해제 후 정지.
        fake.open_canvas.assert_called_once_with(TUK_WIDTH, TUK_HEIGHT)
        fake.close_canvas.assert_called_once()
        for exit_event in (event(1, 14), event(0)):
            fake.get_events.side_effect = [[exit_event]]
            fake.close_canvas.reset_mock()
            with patch.dict(sys.modules, {'pico2d': fake}):
                app.main()
            fake.close_canvas.assert_called_once()
        fake.load_image.side_effect = OSError('이미지 로드 실패')
        fake.close_canvas.reset_mock()
        with patch.dict(sys.modules, {'pico2d': fake}), self.assertRaises(OSError):
            app.main()
        fake.close_canvas.assert_called_once()
        fake.open_canvas.reset_mock()
        with patch.dict(sys.modules, {'pico2d': fake}), patch.object(
            app, 'ASSET_DIR', app.ASSET_DIR / 'missing'
        ), self.assertRaisesRegex(FileNotFoundError, 'TUK_GROUND.png'):
            app.main()
        fake.open_canvas.assert_not_called()


if __name__ == '__main__':
    unittest.main()
