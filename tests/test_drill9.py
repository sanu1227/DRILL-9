"""실행: python -m unittest discover -s tests -v (창을 열지 않음)."""

from math import hypot
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'DRILL_09'))
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


if __name__ == '__main__':
    unittest.main()
