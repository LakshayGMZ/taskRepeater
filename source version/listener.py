from pynput import mouse, keyboard
from pynput.keyboard import Key, KeyCode
import time
import ctypes
import platform


class InputListener:
    def __init__(self):
        self.mouseListener = mouse.Listener(on_click=self.on_click)
        self.keyBoardListener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.system_platform = platform.system()
        if self.system_platform == "Windows":
            self.scaleFactor = float(ctypes.windll.shcore.GetScaleFactorForDevice(0)) / 100
        else:
            self.scaleFactor = 1

        self.timer = time.time()
        self.inputList = []

    def on_click(self, x, y, button, pressed):
        if pressed:
            # print(f'Clicked at ({x}, {y}) with {button}')
            self.inputList.append({"inputType": "sleep", "time": round(time.time() - self.timer, 2)})
            self.inputList.append(
                {"inputType": "mouse", "pos": (x / self.scaleFactor, y / self.scaleFactor), "button": button})
            self.timer = time.time()

    def on_press(self, key: Key):
        try:
            pressedKey = self.keyBoardListener.canonical(key)
            specialKey = False
        except AttributeError:
            pressedKey = f"Key.{key.name}"
            specialKey = True
            # print(f'Special key pressed: {key.value}')
        self.inputList.append({"inputType": "sleep", "time": round(time.time() - self.timer, 2)})
        self.inputList.append({"inputType": "keyPress", "key": pressedKey, "specialKey": specialKey})
        self.timer = time.time()

    def on_release(self, key: Key | KeyCode | None):
        try:
            pressedKey = self.keyBoardListener.canonical(key)
            specialKey = False
            # print(f'Key pressed: {key.char}')
        except AttributeError:
            pressedKey = f"Key.{key.name}"
            specialKey = True
            # print(f'Special key pressed: {key.value}')
        self.inputList.append({"inputType": "sleep", "time": time.time() - self.timer})
        self.inputList.append({"inputType": "keyRelease", "key": pressedKey, "specialKey": specialKey})
        self.timer = time.time()

    def startListening(self):
        print("starting")
        self.timer = time.time()

        if self.system_platform == 'Darwin':
            self.keyBoardListener.run()
            self.mouseListener.run()

        elif self.system_platform == 'Windows':
            self.keyBoardListener.start()
            self.mouseListener.start()

    def stopListening(self):
        if self.system_platform == 'Windows':
            self.keyBoardListener.stop()
            self.mouseListener.stop()
        else:
            pass

    def reset(self):
        self.stopListening()
        self.mouseListener = mouse.Listener(on_click=self.on_click)
        self.keyBoardListener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.inputList = []
