import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import *
from tkinter import colorchooser
from dep.ui_builder import *
import dep.ui_builder as bld
import dep.file_builder as fls
from PIL import Image, ImageTk
from pynput import keyboard

workspaceSize = Vector2(500, 400)

toolbarWidth = 201

ImageLibrary = {
    "workspace" : Image.open("icons/workspace.png"),
    "<class 'tkinter.Label'>" : Image.open("icons/label.png"),
    "<class 'tkinter.Frame'>" : Image.open("icons/frame.png"),
    "<class 'tkinter.Button'>" : Image.open("icons/button.png"),
    "<class 'tkinter.LabelFrame'>" : Image.open("icons/labelFrame.png"),
    "<class 'tkinter.Entry'>" : Image.open("icons/entry.png"),
    "<class 'tkinter.Radiobutton'>" : Image.open("icons/radio.png"),
    "<class 'tkinter.Checkbutton'>" : Image.open("icons/checkbutton.png")
}

root = Tk()
style = ttk.Style()

root.title("DragDropTK")
root.iconbitmap("dragdrop.ico")

root.geometry(str(workspaceSize.x + toolbarWidth + 100) + "x" + str(workspaceSize.y + 100))

workspace = tk.Frame(root, width=workspaceSize.x, height=workspaceSize.y, name="workspace", bg="#f0f0f0")

attributes_list = {}
currentEl = None

defaultFilePath = ''

def resetArgs(el, reset):
    if reset:
        attributes.yview_moveto(0)
    global attributes_list
    global currentEl
    currentEl = el

    elType = str(type(el))

    if el != None:
        if el.winfo_name() == "workspace":
            elType = "workspace"
    
    i = 0
    for x, wt in widgetArgs.items():
        if elType in wt["types"]:
            attributes_list[x]["stringVar"].set(str(bld.getElementArg(el, x)))
            if wt["isColor"]:
                attributes_list[x]["colorBox"].config(bg=str(bld.getElementArg(el, x)))
            if not attributes_list[x]["frame"].winfo_ismapped():
                attributes_list[x]["frame"].grid(row=i, column=0, sticky="ew")
        else:
            attributes_list[x]["frame"].grid_forget()
        i += 1
    
    root.update()
    
    if el == None:
        attributes.config(scrollregion=(0, 0, 0, 0))
    else:
        attributes.config(scrollregion=attributes.bbox('all'))

dnd = DragManager(root, resetArgs, workspace, workspaceSize)

def exportFile():
    path = asksaveasfilename(defaultextension=".py", filetypes=[('Python Files', '*.py')], initialdir="savefiles")

    if path != '':
        file = open(str(path), mode='w')

        file.writelines(fls.generate_file(workspace, workspaceSize, bld, dnd))

        file.close()

def saveAsFile():
    path = asksaveasfilename(defaultextension=".json", filetypes=[('Save File', '*.json')], initialdir="savefiles")
    
    if path != '':
        file = open(str(path), mode='w')

        fls.save_to_json(workspace, workspaceSize, bld, file, dnd)

        file.close()

        global defaultFilePath
        defaultFilePath = path

def saveFile():
    global defaultFilePath
    if defaultFilePath == '':
        defaultFilePath = asksaveasfilename(defaultextension=".json", filetypes=[('Save File', '*.json')], initialdir="savefiles")
    
    if defaultFilePath != '':
        file = open(str(defaultFilePath), mode='w')

        fls.save_to_json(workspace, workspaceSize, bld, file, dnd)

        file.close()

def loadFile():
    path = askopenfile(defaultextension=".json", filetypes=[('Save File', '*.json')], initialdir="savefiles")
    
    if path != None:
        if path.name != '':
            file = open(path.name, mode='r')

            build_lib = fls.load_from_json(file)

            newWorkspace(build_lib["workspace"]["sizex"], build_lib["workspace"]["sizey"], None)
            workspace.config(bg=build_lib["workspace"]["bg"])

            del build_lib["workspace"]

            def extractNumerator(mainType, value):
                cnt = ""
                for char in value["name"]:
                    if char.isnumeric():
                        cnt = cnt + char
                
                if cnt != "":
                    if int(cnt) > widgetCount[mainType]:
                        widgetCount[mainType] = int(cnt)

            for key, value in list(build_lib.items()):
                if value["tkType"] == "StringVar":
                    mainType = value["mainType"]
                
                    # Extract numerator
                    extractNumerator(mainType, value)

                    newObj = tk.StringVar(name=value["name"])
                    newObj.set(value["value"])

                    dnd.add_var(newObj)

                    del build_lib[key]


            for key, value in build_lib.items():
                mainType = value["mainType"]
                
                # Extract numerator
                extractNumerator(mainType, value)
                
                newObj = getattr(tk, value["tkType"])(workspace, name=value["name"])

                del value["tkType"]
                del value["mainType"]

                placeArgs = {
                    "anchor" : CENTER
                }
                configArgs = {}

                #buildFont = {}
                #addFont = False

                # Add widgets

                for x, v in value.items():
                    if x == "font":
                        configArgs[x] = v
                    else:
                        if widgetArgs[x]["inType"] == "config":
                            configArgs[widgetArgs[x]["argName"]] = v
                        elif widgetArgs[x]["inType"] == "place":
                            placeArgs[widgetArgs[x]["argName"]] = v
                        elif widgetArgs[x]["inType"] == "img":
                            if v != '':
                                if v in ImageLibrary.keys():
                                    configArgs['image'] = ImageLibrary[v]
                                    newObj.image_ref = ImageLibrary[v]
                                else:
                                    try:
                                        img1 = tk.PhotoImage(file=v)
                                        ImageLibrary[v] = img1

                                        configArgs['image'] = ImageLibrary[v]
                                        newObj.image_ref = ImageLibrary[v]
                                    except:
                                        configArgs['image'] = ''
                        elif widgetArgs[x]["inType"] == "var":
                            newVar = tk.StringVar()
                            newVar.set(v)
                            newObj.var_ref = newVar
                            newObj.config(textvariable=newVar)


                if mainType == "<class 'tkinter.Entry'>":
                    newObj.config(state="disabled")
                    newObj.place(relwidth=0, relheight=0)
                
                newObj.config(**configArgs)
                newObj.place(**placeArgs)

                dnd.add_draggable(newObj, False)
                addNewWidget(newObj, False)
            
            global defaultFilePath
            defaultFilePath = path.name
            
            root.update()
            widgets.config(scrollregion=widgets.bbox('all'))
            refactor_elements()


def addElement(elType):
    if elType == "Frame":
        widgetCount["<class 'tkinter.Frame'>"] += 1
        newFrame = tk.Frame(workspace, height=64, width=64, name="frame"+str(widgetCount["<class 'tkinter.Frame'>"]))
        newFrame.place(x=int(workspaceSize.x / 2),y=int(workspaceSize.y / 2),anchor=CENTER)

        newFrame.config(bg="#d0d5d9")

        addNewWidget(newFrame, True)
        dnd.add_draggable(newFrame, True)
    if elType == "Label":
        widgetCount["<class 'tkinter.Label'>"] += 1
        newFrame = tk.Label(workspace, text="Label Text", font=("Calibri", 20, "normal"), name="label"+str(widgetCount["<class 'tkinter.Label'>"]))
        newFrame.place(x=int(workspaceSize.x / 2),y=int(workspaceSize.y / 2),anchor=CENTER)

        newFrame.config(bg="#d0d5d9", fg="#1f2326")

        addNewWidget(newFrame, True)
        dnd.add_draggable(newFrame, True)
    if elType == "Button":
        widgetCount["<class 'tkinter.Button'>"] += 1
        newFrame = tk.Button(workspace, text="Button", font=("Calibri", 20, "normal"), name="button"+str(widgetCount["<class 'tkinter.Button'>"]))
        newFrame.place(x=int(workspaceSize.x / 2),y=int(workspaceSize.y / 2), anchor=CENTER, width=128, height=42)

        newFrame.config(bg="#d0d5d9", fg="#1f2326", activebackground="#d0d5d9", activeforeground="#1f2326")

        addNewWidget(newFrame, True)
        dnd.add_draggable(newFrame, True)
    if elType == "LabelFrame":
        widgetCount["<class 'tkinter.LabelFrame'>"] += 1
        newFrame = tk.LabelFrame(workspace, height=64, width=128, text="Frame Text", font=("Calibri", 12, "normal"), name="labelFrame"+str(widgetCount["<class 'tkinter.LabelFrame'>"]))
        newFrame.place(x=int(workspaceSize.x / 2),y=int(workspaceSize.y / 2),anchor=CENTER)

        newFrame.config(bg="#d0d5d9", fg="#1f2326")

        addNewWidget(newFrame, True)
        dnd.add_draggable(newFrame, True)
    if elType == "Entry":
        widgetCount["<class 'tkinter.Entry'>"] += 1
        entryVar = tk.StringVar()
        newFrame = tk.Entry(workspace, font=("Calibri", 12, "normal"), name="entry"+str(widgetCount["<class 'tkinter.Entry'>"]), textvariable=entryVar)
        entryVar.set("Entry field...")

        newFrame.var_ref = entryVar

        newFrame.place(x=int(workspaceSize.x / 2),y=int(workspaceSize.y / 2),anchor=CENTER, relwidth=0, width=128, relheight=0, height=32)

        newFrame.config(bg="#d0d5d9", fg="#1f2326", state="disabled", disabledbackground="#d0d5d9", disabledforeground="#1f2326")

        addNewWidget(newFrame, True)
        dnd.add_draggable(newFrame, True)
    if elType == "Radio":
        widgetCount["<class 'tkinter.Radiobutton'>"] += 1

        if len(dnd.all_vars) == 0:
            widgetCount["<class 'tkinter.StringVar'>"] += 1
            entryVar = tk.StringVar(name="stringVar"+str(widgetCount["<class 'tkinter.StringVar'>"]))
            entryVar.set("1")
            dnd.add_var(entryVar)
        
        newFrame = tk.Radiobutton(workspace, font=("Calibri", 12, "normal"), name="radioButton"+str(widgetCount["<class 'tkinter.Radiobutton'>"]), variable=dnd.all_vars[0], text="Radio Button", value="0")

        newFrame.place(x=int(workspaceSize.x / 2),y=int(workspaceSize.y / 2),anchor=CENTER, relwidth=0, width=128, relheight=0, height=32)

        newFrame.config(bg="#d0d5d9", fg="#1f2326", state="normal", activeforeground="#1f2326", activebackground="#d0d5d9")

        addNewWidget(newFrame, True)
        dnd.add_draggable(newFrame, True)
    if elType == "Check":
        if len(dnd.all_vars) == 0:
            widgetCount["<class 'tkinter.StringVar'>"] += 1
            entryVar = tk.StringVar(name="stringVar"+str(widgetCount["<class 'tkinter.StringVar'>"]))
            entryVar.set("off")
            dnd.add_var(entryVar)

        widgetCount["<class 'tkinter.Checkbutton'>"] += 1
        newFrame = tk.Checkbutton(workspace, font=("Calibri", 12, "normal"), name="checkButton"+str(widgetCount["<class 'tkinter.Checkbutton'>"]), variable=dnd.all_vars[0], offvalue="off", onvalue="on", text="Check Button")

        newFrame.var_ref = dnd.all_vars[0]

        newFrame.place(x=int(workspaceSize.x / 2),y=int(workspaceSize.y / 2),anchor=CENTER, relwidth=0, width=128, relheight=0, height=32)

        newFrame.config(bg="#d0d5d9", fg="#1f2326", activebackground="#d0d5d9", activeforeground="#1f2326")

        addNewWidget(newFrame, True)
        dnd.add_draggable(newFrame, True)
    if elType == "Var":
        widgetCount["<class 'tkinter.StringVar'>"] += 1
        entryVar = tk.StringVar(name="stringVar"+str(widgetCount["<class 'tkinter.StringVar'>"]))
        entryVar.set("1")
        dnd.add_var(entryVar)

def getVarFromStr(string):
    for v in dnd.all_vars:
        if string == str(v):
            return v
    return None

def setArg(var=None, argName=None, atype=None, directVar=None):
    global currentEl
    if currentEl != None:
        root.focus()
        v = directVar or var.get()

        if atype == "string":
            v = str(v)
        elif atype == "int":
            v = int(v)
        elif atype == "var":
            v = getVarFromStr(v)
        
        if widgetArgs[argName]["inType"] == "place":
            currentEl.place(**{widgetArgs[argName]["argName"] : v, "anchor" : CENTER})
        elif widgetArgs[argName]["inType"] == "config":
            currentEl.config(**{widgetArgs[argName]["argName"] : v})
        elif widgetArgs[argName]["inType"] == "img":
            if v == '':
                currentEl.config(image='')
            else:
                try:
                    img1 = None
                    if v in ImageLibrary.keys():
                        img1 = ImageLibrary[v]
                    else:
                        img1 = tk.PhotoImage(file=v)
                        ImageLibrary[v] = img1
                    
                    currentEl.config(image=img1)
                    currentEl.image_ref = img1
                except:
                    currentEl.config(image='')
                    var.set("")
        elif widgetArgs[argName]["inType"] == "fontc":
            currentFont = currentEl.cget("font")
            if currentFont[0] == "{":
                currentFont = currentFont[1:]
                currentFont = currentFont.split("}")
                currentFont = [currentFont[0], currentFont[1].split(" ")[1], currentFont[1].split(" ")[2]]
            else:
                currentFont = currentFont.split(" ")
            
            if argName == "font-family":
                currentEl.config(font=(v, int(currentFont[1]), currentFont[2]))
            elif argName == "font-size":
                currentEl.config(font=(currentFont[0], int(v), currentFont[2]))
            else: 
                currentEl.config(font=(currentFont[0], int(currentFont[1]), v))
        elif widgetArgs[argName]["inType"] == "var":
            currentEl.var_ref.set(v)
        
        inName = widgetArgs[argName]["argName"]

        root.update()

        if currentEl.winfo_name() != "workspace":
            dnd.align_box(currentEl, "select")

        if argName == "x" or argName == "y":
            refactor_elements(w=currentEl)

        if widgetArgs[argName]["isColor"]:
            attributes_list[argName]["colorBox"].config(bg=v)


def openColorPicker(attributeName, type, sVar):
    global currentEl
    color_code = colorchooser.askcolor(title="Set color for " + attributeName, color=getElementArg(currentEl, attributeName))
    if color_code[1] != None:
        setArg(argName=attributeName, atype=type, directVar=color_code[1])
        sVar.set(str(color_code[1]))

def addNewArg(argName, parent, type):
    sVar = tk.StringVar()
    sVar.set('0')

    setName = widgetArgs[argName]["argName"]
    if "saveName" in widgetArgs[argName].keys():
        setName = widgetArgs[argName]["saveName"]

    newFrame = tk.Frame(parent, height=12, pady=1,  bg="#252d36")
    newBox = None 
    if argName == "variable":
        newBox = ttk.Combobox(newFrame, textvariable=sVar)
        dnd.set_combobox(newBox)
        newBox.config(width=14)
    else:
        newBox = tk.Entry(newFrame, textvariable=sVar)
        newBox.config(width=18)
        
    newLabel = tk.Label(newFrame, text=setName, bg="#252d36", fg="white")
    newLabel.config(width=8)

    newLabel.pack(side=LEFT, padx=1)

    colorPicker = None
    if widgetArgs[argName]["isColor"]:
        colorPicker = tk.Frame(newFrame, bg="white", width=18, height=18, highlightthickness=1, highlightbackground="#1a1e24", cursor="hand2")
        colorPicker.pack(side=LEFT, padx=(4,2))

        newBox.config(width=14)
    newBox.pack(side=LEFT, padx=(4, 4))

    if widgetArgs[argName]['inType'] == "None":
        newBox.config(state="readonly")

    global attributes_list
    attributes_list[argName] = {
        "stringVar" : sVar,
        "frame" : newFrame,
        "colorBox" : colorPicker,
        "entry" : newBox
    }

    if colorPicker != None:
        colorPicker.bind("<ButtonRelease-1>", lambda event: openColorPicker(argName, type, sVar))
    
    if argName == "variable":
        newBox.bind("<<ComboboxSelected>>", lambda event: setArg(sVar, argName, type))
    newBox.bind("<Return>", lambda event: setArg(sVar, argName, type))

def addNewWidget(widget, ru):
    newFrame = tk.Frame(widgets_frame, height=24,  bg="#252d36",width=184)
    newLabel = tk.Label(newFrame, text=widget.winfo_name(), bg="#252d36", fg="white", font=("Calibri", 10, "normal"))
    newLabel.config(height=24)


    newImage = None
    if widget.winfo_name() == "workspace":
        newImage = ImageTk.PhotoImage(ImageLibrary["workspace"])
    else:
        newImage = ImageTk.PhotoImage(ImageLibrary[str(type(widget))])

    newImgLabel = Label(newFrame, image=newImage, bg="#252d36", height=24)
    newImgLabel.image = newImage
    
    newImgLabel.pack(side=LEFT, padx=3, pady=4)
    newLabel.pack(side=LEFT, padx=5)
    newFrame.pack(side=TOP, fill="x")
    newFrame.pack_propagate(False)

    dnd.add_widgetselector([newFrame, newLabel, newImgLabel], widget)

    if ru:
        root.update()
    
    widgets.config(scrollregion=widgets.bbox('all'))

def newWorkspace(xres, yres, toplevel):
    if int(xres) > 0 and int(yres) > 0:
        dnd.destroy_workspace(int(xres), int(yres))
        resetArgs(None, True)

        if toplevel != None:
            toplevel.destroy()
            global defaultFilePath
            defaultFilePath = ''
            workspace.config(bg="#F0F0F0")

        global workspaceSize
        oldscreenSize_x, oldscreenSize_y = root.winfo_width() - toolbarWidth - 100, root.winfo_height() - 100
        workspaceSize.set(int(xres), int(yres))

        if workspaceSize.x > oldscreenSize_x:
            oldscreenSize_x = workspaceSize.x
        if workspaceSize.y > oldscreenSize_y:
            oldscreenSize_y = workspaceSize.y

        root.geometry(str(oldscreenSize_x + toolbarWidth + 100) + "x" + str(oldscreenSize_y + 100))
        workspace.config(width=workspaceSize.x, height=workspaceSize.y)

        resize(None, True)

        indicator_x.config(text=str(workspaceSize.x) + "px")
        indicator_y.config(text=str(workspaceSize.y) + "px")

def resetWorkspace():
    new_window = tk.Toplevel()
    new_window.resizable(False, False)
    new_window.iconbitmap("dragdrop.ico")
    new_window.title("New File")
    new_window.geometry("250x128")

    new_window.config(bg="#2b313b")

    main_frame = tk.Frame(new_window, bg="#1a1e24")
    main_label = ttk.Label(main_frame, text="New File", font=("Calibri", 14, "normal"), background="#1a1e24", foreground="white")

    bottom_frame = tk.Frame(new_window, bg="#1a1e24")

    bottom_frame.pack(fill=BOTH, expand=True, padx=2, pady=2, side=BOTTOM)
    main_frame.pack(pady=(2, 0), padx=2, fill="x")
    main_label.pack()

    option1_frame = tk.Frame(bottom_frame, bg="#1a1e24")
    option1_label = tk.Label(option1_frame, text="Resolution X", font=("Calibri", 12, "normal"), bg="#1a1e24", fg="white")
    res_x = StringVar()
    res_x.set(500)
    option1_textbox = tk.Entry(option1_frame, textvariable=res_x, font=("Calibri", 12, "normal"))

    option1_frame.pack(padx=2, pady=2, fill="x")
    option1_label.pack(side=LEFT, padx=2)
    option1_textbox.pack(side=LEFT, padx=2)

    option2_frame = tk.Frame(bottom_frame, bg="#1a1e24")
    option2_label = tk.Label(option2_frame, text="Resolution Y", font=("Calibri", 12, "normal"), bg="#1a1e24", fg="white")
    res_y = StringVar()
    res_y.set(400)
    option2_textbox = tk.Entry(option2_frame, textvariable=res_y, font=("Calibri", 12, "normal"))

    option2_frame.pack(padx=2, pady=2, fill="x")
    option2_label.pack(side=LEFT, padx=2)
    option2_textbox.pack(side=LEFT, padx=2)

    create_button = tk.Button(bottom_frame, text="Create File", font=("Calibri", 12, "normal"), command=lambda: newWorkspace(res_x.get(), res_y.get(), new_window))
    create_button.pack(pady=3)


class InputManager():
    def __init__(self):
        self.control_down = False

    def on_release(self, key):
        if key == keyboard.Key.delete:
            dnd.remove_selected_widget()
            widgets.config(scrollregion=widgets.bbox('all'))
        if key == keyboard.Key.page_up:
            dnd.zindex_selected_widget(True)
        if key == keyboard.Key.page_down:
            dnd.zindex_selected_widget(False)
    
    def on_duplicate(self):
        dnd.duplicate_selected_widget(addNewWidget)
        widgets.config(scrollregion=widgets.bbox('all'))

    def on_press(self, key):
        pass
    

tools = tk.Frame(root, width=toolbarWidth, height=workspaceSize.y, padx=2, pady=2)
tools.config(bg="#2b313b", highlightbackground="#1a1e24", highlightthickness=0)

attributes = tk.Canvas(tools, width=toolbarWidth, height=int((workspaceSize.y - 4) * 0.5), highlightthickness=0, bg="#1a1e24")
attributes_label = ttk.Label(tools, text="Attributes", font=("Calibri", 12, "normal"), background="#1a1e24", foreground="white")
attributes_scrollbar = ttk.Scrollbar(attributes, orient="vertical",command=attributes.yview)
attributes.config(yscrollcommand=attributes_scrollbar.set)

attributes_packer = tk.Frame(attributes, bg="#1a1e24")

widgets = tk.Canvas(tools, width=toolbarWidth, height=int((workspaceSize.y - 4) * 0.4), highlightthickness=0, bg="#1a1e24")
widgets_label = ttk.Label(tools, text="Widgets", font=("Calibri", 12, "normal"), background="#1a1e24", foreground="white")
widgets_scrollbar = ttk.Scrollbar(widgets, orient="vertical",command=widgets.yview)
widgets.config(yscrollcommand=widgets_scrollbar.set)

settings = tk.Frame(tools, width=toolbarWidth, height=24, highlightthickness=0, bg="#1a1e24")
settings_label = ttk.Label(tools, text="Settings", font=("Calibri", 12, "normal"), background="#1a1e24", foreground="white")

snapto = IntVar()
snapto.set(1)
snapto_checkbox = tk.Checkbutton(settings, text="Snap", highlightthickness=0, variable=snapto, onvalue=1, offvalue=0, font=("Calibri", 10, "normal"), bg="#1a1e24", fg="white", selectcolor="#1a1e24", activebackground="#1a1e24", activeforeground="gray")
snapto_checkbox.config(command=lambda: dnd.change_settings("snap", snapto.get()))

indicator_x = tk.Label(root, fg="#494e54", text="500px", font=("Calibri", 15, "normal"), bg="#101317")
indicator_y = tk.Label(root, fg="#494e54", text="400px", font=("Calibri", 15, "normal"), bg="#101317", wraplength=1)

menubar = Menu(root)

file = Menu(menubar, tearoff = 0)
menubar.add_cascade(label = 'File', menu = file)
file.add_command(label ='New', command= lambda: resetWorkspace())
file.add_command(label ='Save As', command= lambda: saveAsFile())
file.add_command(label ='Save', command= lambda: saveFile())
file.add_command(label ='Load', command= lambda: loadFile())
file.add_command(label ='Export', command= lambda: exportFile())

add = Menu(menubar, tearoff = 0)
menubar.add_cascade(label ='Add', menu = add)
add.add_command(label ='Frame', command = lambda: addElement("Frame"))
add.add_command(label ='LabelFrame', command = lambda: addElement("LabelFrame"))
add.add_command(label ='Label', command = lambda: addElement("Label"))
add.add_command(label ='Button', command = lambda: addElement("Button"))
add.add_command(label ='Entry', command = lambda: addElement("Entry"))
add.add_command(label ='RadioButton', command = lambda: addElement("Radio"))
add.add_command(label ='CheckButton', command = lambda: addElement("Check"))
add.add_command(label ='Variable', command = lambda: addElement("Var"))


tools.pack(side=RIGHT, fill="both")
workspace.place(x=0, y=0, anchor=NW)

attributes_scrollbar.pack(side=RIGHT, fill="y")
attributes.pack(side=BOTTOM, fill="x")
attributes_label.pack(side=BOTTOM, fill="x")
attributes_packer.pack(side=LEFT, fill="both")

attributes.grid_propagate(False)
attributes.pack_propagate(False)


attributes_frame = Frame(attributes, bg="#1a1e24")
attributes.create_window((0, 0), window=attributes_frame, anchor="nw")

for x, wt in widgetArgs.items():
    addNewArg(x, attributes_frame, wt["argType"])

settings_label.pack(side=TOP, fill="x")
settings.pack(side=TOP, fill="x", pady=(0,2))
settings.pack_propagate(False)

snapto_checkbox.pack(side=LEFT, padx=2)

widgets_scrollbar.pack(side=RIGHT, fill="y")
widgets_label.pack(side=TOP, fill="x")
widgets.pack(side=TOP, fill="x", pady=(0,2))
widgets.pack_propagate(False)

widgets_frame = Frame(widgets, bg="#1a1e24")
widgets.create_window((0,0), window=widgets_frame, anchor="nw")

addNewWidget(workspace, True)

root.update()

attributes.config(scrollregion=attributes.bbox('all'))
attributes.yview_moveto(0)

widgets.config(scrollregion=widgets.bbox('all'))
widgets.yview_moveto(0)

inpt = InputManager()
listener = keyboard.Listener(on_release=inpt.on_release, on_press=inpt.on_press)
listenerHotkeys = keyboard.GlobalHotKeys({'<ctrl>+d': inpt.on_duplicate})
listener.start()
listenerHotkeys.start()

old_width, old_height = root.winfo_width(), root.winfo_height()

def resize(event, force=False):
    global old_height, old_width
    if root.winfo_width() != old_width or root.winfo_height() != old_height or force:
        attributes.config(height=int((root.winfo_height() - 4) * 0.5))
        widgets.config(height=int((root.winfo_height() - 4) * 0.5))
        workspace.place(x=int((root.winfo_width() - toolbarWidth) / 2), y=int(root.winfo_height() / 2), anchor=CENTER)

        indicator_x.place(anchor=S, x=int((root.winfo_width() - toolbarWidth) / 2), y=int((root.winfo_height() - workspaceSize.y) / 2))
        indicator_y.place(anchor=E, x=int((root.winfo_width() - workspaceSize.x - toolbarWidth) / 2), y=int(root.winfo_height() / 2))

        old_width, old_height = root.winfo_width(), root.winfo_height()

root.bind("<Configure>", resize)
root.config(menu=menubar, bg="#101317")
root.resizable(True, True)
root.mainloop()