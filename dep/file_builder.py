import tkinter as tk
from tkinter import *
import json
import os.path

def generate_file(workspace, size, bld):
    main_code = []

    main_code.append('''import tkinter as tk
from tkinter import *
                
root = Tk()\n
root.title("My Window")
root.resizable(False, False)''')
    
    main_code.append('\nroot.geometry("' + str(size.x) + "x" + str(size.y) + '")')
    main_code.append('\nroot.config(bg="'+ workspace.cget('bg') +'")\n')
    
    main_code.append('\n# Button functions\n')

    main_code.append('\n# Adding widgets\n')
    
    image_objects = []

    images_block = "\n_images = {"

    for widget in workspace.winfo_children():
        if widget.winfo_name() != "barx" and widget.winfo_name() != "bary":
            elType = str(type(widget))

            newline = "\n" + widget.winfo_name() + " = tk." + str(elType[16:][:-2]) +"(root"
            newline1 = "\n" + widget.winfo_name() + ".place(anchor=CENTER"

            buildFont = {}
            useFont = False

            for x, wt in bld.widgetArgs.items():
                if elType in wt["types"]:
                    v = bld.getElementArg(widget, x)
                    oldV = v
                    if isinstance(v, str):
                        v = '"'+ str(v) +'"'
                    
                    if wt["inType"] == "None" or wt["inType"] == "config":
                        newline = newline + ", " + x + "=" + str(v)
                    if wt["inType"] == "place":
                        newline1 = newline1 + ", " + x + "=" + str(v)
                    if wt["inType"] == "fontc":
                        buildFont[x] = str(v)
                        useFont = True
                    if wt["inType"] == "img":
                        if oldV != '':
                            if oldV in image_objects:
                                newline = newline + ", image=_images[" + v + "]"
                            else:
                                image_objects.append(str(oldV))
                                images_block = images_block + "\n\t" + v + " : " + "tk.PhotoImage(file='" + oldV + "'),"
                                newline = newline + ", image=_images[" + v + "]"


            if useFont:
                newline = newline + ", font=(" + buildFont["font-family"] + ", " + buildFont["font-size"] + ", " + buildFont["font-type"] + ")"

            if type(widget) == tk.Button:
                newline = newline + ", command=press_" + widget.winfo_name()

                main_code.insert(4, "\tprint('" + widget.winfo_name() + " pressed!')\n")
                main_code.insert(4, "\ndef " + "press_" + widget.winfo_name() + "():\n")

            newline = newline + ")"
            newline1 = newline1 + ")\n"

            main_code.append(newline)
            main_code.append(newline1)

    images_block = images_block + "}\n"

    main_code.insert(3, images_block)

    main_code.append("\nroot.mainloop()")


    return main_code

def load_from_json(file):
    return json.load(file)

def save_to_json(workspace, size, bld, file):

    data = {
        "workspace" : {
            "sizex" : size.x,
            "sizey" : size.y,
            "bg" : workspace.cget("bg")
        }
    }

    for widget in workspace.winfo_children():
        if widget.winfo_name() != "barx" and widget.winfo_name() != "bary":
            elType = str(type(widget))
            mainKey = widget.winfo_name()

            data[mainKey] = {}

            buildFont = {}
            useFont = False

            for x, wt in bld.widgetArgs.items():
                if elType in wt["types"]:
                    v = bld.getElementArg(widget, x)
                    
                    if wt["inType"] == "None" or wt["inType"] == "config":
                        data[mainKey][x] = v
                    if wt["inType"] == "place":
                        data[mainKey][x] = v
                    if wt["inType"] == "fontc":
                        buildFont[x] = str(v)
                        useFont = True
                    if wt["inType"] == "img":
                        data[mainKey][x] = v

            if useFont:
                data[mainKey]["font"] = (buildFont["font-family"], buildFont["font-size"], buildFont["font-type"])
            
            data[mainKey]["tkType"] = elType[16:][:-2]
            data[mainKey]["mainType"] = elType

    
    json.dump(data, file)

    return True