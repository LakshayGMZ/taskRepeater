import os
import tkinter as tk
from tkinter import filedialog

from Settings import DataStorage
from controller import InputController
from listener import InputListener
import keyboard
import configparser


class MainApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.settings = DataStorage()
        self.configParser = configparser.ConfigParser()
        self.configParser.read('shortcuts.ini')
        self.shortcuts = self.configParser['SHORTCUTS']
        if self.settings.data == {}:
            self.settings.create_record("keepOnTop", False)
            self.settings.create_record("playbackSpeed", 1)
            self.settings.create_record("loops", 1)

        self.listener = InputListener()
        self.controller = InputController(settings=self.settings, onStop=self.stopRecording)

        self.startButton = None
        self.stopButton = None
        self.playButton = None
        self.saveButton = None
        self.loadButton = None

        self.keepOnTop = self.settings.data["keepOnTop"]
        self.inputFrame = tk.Frame()
        self.topSettingsFrame = tk.Frame()
        self.topSettingsFrame2 = tk.Frame()

        self.draw()
        self.createBindings()

    def draw(self):
        self.root.title("Task Repeater")
        self.root.resizable(width=False, height=False)
        self.root.attributes('-topmost', self.keepOnTop)

        check_var = tk.BooleanVar(value=self.keepOnTop)
        loopVar = tk.BooleanVar(value=bool(self.settings.data["loops"] == -1))

        def on_checkbox_click():
            if check_var.get():
                self.settings.update_record("keepOnTop", True)
            else:
                self.settings.update_record("keepOnTop", False)
            self.root.attributes('-topmost', self.settings.data["keepOnTop"])

        def onLoopCheckBoxClick():
            if loopVar.get():
                self.settings.update_record("loops", -1)
                loopSaveButton.config(state=tk.DISABLED)
            else:
                self.settings.update_record("loops", 1)
                loopSaveButton.config(state=tk.NORMAL)

        checkbox = tk.Checkbutton(self.topSettingsFrame, text="Keep on Top", variable=check_var,
                                  command=on_checkbox_click)
        checkbox.pack(pady=5, side=tk.TOP)
        tk.Label(self.topSettingsFrame, text="Playback Speed(0.25-5x)").pack(side=tk.LEFT)
        playbackInput = tk.Entry(self.topSettingsFrame, width=7)
        playbackInput.insert(0, self.settings.data["playbackSpeed"])
        playbackInput.pack(side=tk.LEFT)
        tk.Button(self.topSettingsFrame, text="Set",
                  command=lambda: self.settings.update_record("playbackSpeed",
                                                              float(playbackInput.get()))).pack(side=tk.LEFT)
        self.topSettingsFrame.pack()

        tk.Checkbutton(self.topSettingsFrame2, text="Loop infinitely", variable=loopVar,
                       command=onLoopCheckBoxClick).pack(side=tk.RIGHT)

        tk.Label(self.topSettingsFrame2, text="How many times to loop:").pack(side=tk.LEFT)
        inputLoop = tk.Entry(self.topSettingsFrame2, width=7)
        inputLoop.insert(0, self.settings.data['loops'])
        inputLoop.pack(side=tk.LEFT)
        loopSaveButton = tk.Button(self.topSettingsFrame2, text="Save",
                                   command=lambda: self.settings.update_record("loops", inputLoop.get()))
        if self.settings.data['loops'] == -1:
            loopSaveButton.config(state=tk.DISABLED)
        loopSaveButton.pack(side=tk.LEFT)
        self.topSettingsFrame2.pack(after=self.topSettingsFrame)

        imageStart = tk.PhotoImage(file='assets/recButton.png')
        imageStop = tk.PhotoImage(file='assets/stopButton.png')
        imagePlay = tk.PhotoImage(file='assets/playButton.png')
        imageSave = tk.PhotoImage(file='assets/saveButton.png')
        imageLoad = tk.PhotoImage(file='assets/loadButton.png')

        buttonFrame = tk.Frame(self.root)
        buttonFrame.pack()

        self.startButton = tk.Button(buttonFrame, text="Start", image=imageStart, compound=tk.TOP,
                                     command=self.startRecording)
        self.startButton.image = imageStart
        self.startButton.config(state=tk.NORMAL)
        self.startButton.pack(pady=10, padx=5, side=tk.LEFT)

        self.stopButton = tk.Button(buttonFrame, text="Stop", image=imageStop, compound=tk.TOP,
                                    command=lambda: self.stopRecording("button"))
        self.stopButton.image = imageStop
        self.stopButton.config(state=tk.DISABLED)
        self.stopButton.pack(pady=10, padx=5, side=tk.LEFT)

        self.playButton = tk.Button(buttonFrame, text="Play", image=imagePlay, compound=tk.TOP,
                                    command=self.playRecording)
        self.playButton.image = imagePlay
        self.playButton.config(state=tk.DISABLED)
        self.playButton.pack(pady=10, padx=5, side=tk.LEFT)

        self.saveButton = tk.Button(buttonFrame, text="Save", image=imageSave, compound=tk.TOP,
                                    command=self.toggleSaveButton)
        self.saveButton.image = imageSave
        self.saveButton.config(state=tk.DISABLED)
        self.saveButton.pack(pady=10, padx=5, side=tk.LEFT)

        self.loadButton = tk.Button(buttonFrame, text="Load", image=imageLoad, compound=tk.TOP,
                                    command=self.load_file_dialog)
        self.loadButton.image = imageLoad
        self.loadButton.config(state=tk.NORMAL)
        self.loadButton.pack(pady=10, padx=5, side=tk.LEFT)

        # self.inputFrame.pack(side=tk.LEFT, pady=5)

        label = tk.Label(self.inputFrame, text="File name to save:")
        label.pack(side=tk.LEFT, padx=5)

        fileName = tk.Entry(self.inputFrame, width=14)
        fileName.pack(side=tk.LEFT)

        label = tk.Label(self.inputFrame, text="Slot(1-9)")
        label.pack(side=tk.LEFT, padx=5)

        slotNum = tk.Entry(self.inputFrame, width=5)
        slotNum.pack(side=tk.LEFT)

        tk.Button(self.inputFrame, text="Save", command=lambda: self.saveRecording(fileName.get(), slotNum.get())).pack(
            side=tk.LEFT)
        self.inputFrame.pack()

    def run(self):
        self.root.mainloop()

    def on_button_click(self):
        print("hmm")

    def _load_file_dialog(self):
        return filedialog.askopenfilename(initialdir=os.path.join(os.getcwd(), "actions"),
                                          title="Select an Action file",
                                          filetypes=[("Action files", "*.pkl")])

    def load_file_dialog(self, fileName=None):
        if not fileName:
            fileName = self._load_file_dialog()

        self.listener.reset()
        self.listener.inputList = DataStorage(fileName).data['actions']
        self.startButton['state'] = tk.DISABLED
        self.stopButton['state'] = tk.DISABLED
        self.playButton['state'] = tk.NORMAL
        self.saveButton['state'] = tk.NORMAL
        self.loadButton['state'] = tk.NORMAL
        return True

    def startRecording(self, *args):
        self.startButton['state'] = tk.DISABLED
        self.stopButton['state'] = tk.NORMAL
        self.playButton['state'] = tk.DISABLED
        self.saveButton['state'] = tk.DISABLED
        self.loadButton['state'] = tk.DISABLED

        self.listener.reset()
        self.listener.startListening()

    def stopRecording(self, target, *args):
        self.startButton['state'] = tk.NORMAL
        self.stopButton['state'] = tk.DISABLED
        self.playButton['state'] = tk.NORMAL
        self.saveButton['state'] = tk.NORMAL
        self.loadButton['state'] = tk.NORMAL

        self.listener.stopListening()
        self.controller.forceQuit = True
        if target == "hotkey":
            print("hotkey!")
            self.listener.inputList = self.listener.inputList[0:(-2*len(self.shortcuts["SHORTCUT_STOP"].split('+'))+1)]
        if target == "button":
            self.listener.inputList = self.listener.inputList[0:-1]

    def playRecording(self, *args):
        self.startButton['state'] = tk.DISABLED
        self.stopButton['state'] = tk.NORMAL
        self.playButton['state'] = tk.DISABLED
        self.saveButton['state'] = tk.DISABLED
        self.loadButton['state'] = tk.DISABLED

        self.controller.forceQuit = False
        self.controller.startControlling(self.listener.inputList)

    def toggleSaveButton(self):
        if self.inputFrame.winfo_ismapped():
            self.inputFrame.pack_forget()
        else:
            self.inputFrame.pack()

    def saveRecording(self, fileName, slotNum: int, *args):
        newAction = DataStorage(f"actions/{fileName}.{str(slotNum)}.pkl")
        newAction.create_record("name", "action")
        newAction.create_record("actions", self.listener.inputList)
        newAction.create_record("slot", slotNum)
        self.inputFrame.pack_forget()

    def getFileName(self, slot: int):
        files_and_directories = os.listdir("actions")

        all_files = [f for f in files_and_directories if
                     (os.path.isfile(os.path.join("actions", f)) and f[0] != "." and f.split(".")[-2].isnumeric())]

        filteredFile = [f for f in all_files if int(f.split(".")[-2]) == slot]
        if len(filteredFile) == 0:
            return None
        return "actions/" + filteredFile[0]

    def onHotKeyPressed(self, action, slotNum=-1):
        if action == "Slot":
            print("Slot " + str(slotNum) + " called")
            fileName = self.getFileName(slotNum)
            print(fileName)
            if fileName is not None:
                self.load_file_dialog(fileName)
                self.playRecording()

    def createBindings(self):
        keyboard.add_hotkey(self.shortcuts["SHORTCUT_SLOT_1"], self.onHotKeyPressed, ("Slot", 1))
        keyboard.add_hotkey(self.shortcuts["SHORTCUT_SLOT_2"], self.onHotKeyPressed, ("Slot", 2))
        keyboard.add_hotkey(self.shortcuts["SHORTCUT_SLOT_3"], self.onHotKeyPressed, ("Slot", 3))
        keyboard.add_hotkey(self.shortcuts["SHORTCUT_SLOT_4"], self.onHotKeyPressed, ("Slot", 4))
        keyboard.add_hotkey(self.shortcuts["SHORTCUT_SLOT_5"], self.onHotKeyPressed, ("Slot", 5))
        keyboard.add_hotkey(self.shortcuts["SHORTCUT_SLOT_6"], self.onHotKeyPressed, ("Slot", 6))
        keyboard.add_hotkey(self.shortcuts["SHORTCUT_SLOT_7"], self.onHotKeyPressed, ("Slot", 7))
        keyboard.add_hotkey(self.shortcuts["SHORTCUT_SLOT_8"], self.onHotKeyPressed, ("Slot", 8))
        keyboard.add_hotkey(self.shortcuts["SHORTCUT_SLOT_9"], self.onHotKeyPressed, ("Slot", 9))
        keyboard.add_hotkey(self.shortcuts["SHORTCUT_STOP"], self.stopRecording, ("hotkey",0))
        keyboard.add_hotkey(self.shortcuts["SHORTCUT_RECORD"], self.startRecording)
        # keyboard.wait("esc")
