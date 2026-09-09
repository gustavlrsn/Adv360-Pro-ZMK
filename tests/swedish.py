"""Generate a native ZMK integration test and check its actual HID modifier logs.

Run inside the repository's ZMK build image:
  python3 /repo/tests/swedish.py generate /tmp/swedish-test
  west build -s zmk/app -d /tmp/swedish-build -b native_posix_64 -- \
      -DZMK_CONFIG=/tmp/swedish-test -DCONFIG_ASSERT=y
  /tmp/swedish-build/zephyr/zmk.exe > /tmp/swedish.log
  python3 /repo/tests/swedish.py verify /tmp/swedish.log
"""
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
# Expected USB HID key usages and report modifiers, independent of the behaviors.
LETTERS = [
    ('aa', 0x31, [(0x04, 0x04)], [(0x04, 0x06)]),
    ('oe', 0x33, [(0x18, 0x04), (0x12, 0)], [(0x18, 0x04), (0x12, 0x02)]),
    ('ae', 0x34, [(0x18, 0x04), (0x04, 0)], [(0x18, 0x04), (0x04, 0x02)]),
]


def scenario():
    layers, events, expected = [], [], []

    def event(press, row, col):
        events.append(f'ZMK_MOCK_{"PRESS" if press else "RELEASE"}({row},{col},10)')

    def tap(row, col):
        event(True, row, col)
        event(False, row, col)

    for alt, shift, shift_mod in [
        ('LALT', 'LSHFT', 2), ('RALT', 'RSHFT', 32),
        ('LALT', 'RSHFT', 32), ('RALT', 'LSHFT', 2),
    ]:
        for name, symbol, lower, upper in LETTERS:
            index = len(layers)
            layers.append(f'layer_{index} {{ bindings = <&kp {alt} &sw_{name} &kp {shift} &to {(index+1)%12}>; }};')
            # US, Shift+US, Option, Option+Shift. Repeat letters while held.
            for option, capital in [(False, False), (False, True), (True, False), (True, True)]:
                if option:
                    event(True, 0, 0)
                if capital:
                    event(True, 1, 0)
                repeats = 2 if option else 1
                for _ in range(repeats):
                    tap(0, 1)
                    expected.extend(upper if option and capital else lower if option else [(symbol, shift_mod if capital else 0)])
                if capital:
                    event(False, 1, 0)
                if option:
                    event(False, 0, 0)
            # Release Option before the target, then immediately type US again.
            event(True, 0, 0)
            event(True, 0, 1)
            expected.extend(lower)
            event(False, 0, 0)
            event(False, 0, 1)
            tap(0, 1)
            expected.append((symbol, 0))
            tap(1, 1)
    return layers, events, expected


def verify_keymap():
    source = (ROOT / 'config/adv360.keymap').read_text().split('    keymap {', 1)[1]
    blocks = re.findall(r'        (\w+) \{\n(.*?)\n        };', source, re.S)
    active = [(name, body) for name, body in blocks if 'status = "reserved"' not in body]
    assert [name for name, _ in active] == ['default_layer', 'unused', 'keypad', 'fn', 'mod']
    bindings = []
    for _, body in active:
        raw = re.search(r'bindings = <(.*?)>;', body, re.S)[1]
        bindings.append([x.strip() for x in re.findall(r'&\w+(?:\s+[^&\s]+)*', raw)])
    assert all(len(layer) == 76 for layer in bindings)
    for index, expected in {27: '&sw_aa', 44: '&sw_oe', 45: '&sw_ae', 20: '&none', 6: '&tog 2', 7: '&mo 4', 60: '&mo 3', 75: '&mo 3'}.items():
        assert bindings[0][index] == expected, (index, bindings[0][index])
    assert json.loads((ROOT / 'config/keymap.json').read_text())['layers'] == bindings


def generate(directory):
    directory.mkdir(parents=True, exist_ok=True)
    layers, events, _ = scenario()
    source = '\n'.join([
        '#include <dt-bindings/zmk/keys.h>', '#include <behaviors.dtsi>',
        '#include <dt-bindings/zmk/kscan_mock.h>',
        f'#include "{ROOT / "config/swedish.dtsi"}"',
        '/ { keymap { compatible = "zmk,keymap";', *layers, '}; };',
        '&kscan { events = <', *events, '>; };', '',
    ])
    (directory / 'native_posix_64.keymap').write_text(source)


def verify(log):
    verify_keymap()
    actual, pending = [], None
    text = log.read_text()
    for line in text.splitlines():
        match = re.search(r'hid_listener_keycode_pressed: usage_page 0x07 keycode 0x([0-9a-fA-F]+)', line)
        if match:
            key = int(match[1], 16)
            pending = key if key < 0xE0 else None
        match = re.search(r'hid_implicit_modifiers_press: Modifiers set to 0x([0-9a-fA-F]+)', line)
        if match and pending is not None:
            actual.append((pending, int(match[1], 16)))
            pending = None
    expected = scenario()[2]
    if actual != expected:
        for i, (a, e) in enumerate(zip(actual, expected)):
            if a != e:
                raise AssertionError(f'HID event {i}: got {a}, expected {e}')
        raise AssertionError(f'Got {len(actual)} HID key presses; expected {len(expected)}')
    assert 'Tried to unregister' not in text and "Can't press the same mod-morph twice" not in text
    print(f'PASS: {len(expected)} HID key presses: US symbols, all six Swedish letters, left/right/crossed modifiers, repeated letters, and release order.')


if __name__ == '__main__':
    if sys.argv[1] == 'generate':
        generate(Path(sys.argv[2]))
    elif sys.argv[1] == 'verify':
        verify(Path(sys.argv[2]))
    else:
        raise SystemExit('Use generate TEST_DIRECTORY or verify LOG_FILE')
