import time
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController, Key
import threading
from Settings import DataStorage

class InputController:
    def __init__(self, settings: DataStorage, onStop):
        self._mouse = MouseController()
        self._keyboard = KeyboardController()

        self.onStop = onStop
        self.settings = settings
        self.forceQuit = False
        self.loopTimes = int(self.settings.data["loops"])
        self.counter = 0

    def _controlLogic(self, inputList):
        while self.loopTimes == -1 or self.counter < self.loopTimes:
            for inputEvent in inputList:
                print(inputEvent)
                if self.forceQuit:
                    break

                if inputEvent['inputType'] == 'keyPress':
                    if inputEvent['specialKey']:
                        self._keyboard.press(eval(inputEvent['key']))
                    else:
                        self._keyboard.press(inputEvent['key'])

                elif inputEvent['inputType'] == 'keyRelease':
                    if inputEvent['specialKey']:
                        self._keyboard.release(eval(inputEvent['key']))
                    else:
                        self._keyboard.release(inputEvent['key'])

                elif inputEvent['inputType'] == 'mouse':
                    self._mouse.position = inputEvent['pos']
                    self._mouse.click(inputEvent['button'], 1)

                elif inputEvent['inputType'] == 'sleep':
                    time.sleep(inputEvent['time']/float(self.settings.data["playbackSpeed"]))

            if self.loopTimes != -1:
                self.counter += 1
        self.onStop("over")
        self.reset()

    def startControlling(self, inputList):
        print("starting controll")
        self.settings.refresh()
        self.loopTimes = int(self.settings.data["loops"])
        self.counter = 0
        threading.Thread(target=self._controlLogic, args=(inputList,)).start()

    def stopControlling(self):
        self.forceQuit = True
    
    def reset(self):
        del self._mouse
        del self._keyboard
        self._mouse = MouseController()
        self._keyboard = KeyboardController()
