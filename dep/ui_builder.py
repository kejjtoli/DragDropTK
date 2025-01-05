from tkinter import *
import tkinter as tk

selectedElement = None

allElements = {}

allSelectors = {}

widgetCount = {
    "<class 'tkinter.Frame'>" : 0,
    "<class 'tkinter.Label'>" : 0,
    "<class 'tkinter.Button'>" : 0,
    "<class 'tkinter.LabelFrame'>" : 0,
    "<class 'tkinter.Entry'>" : 0,
    "<class 'tkinter.Radiobutton'>" : 0,
    "<class 'tkinter.StringVar'>" : 0,
    "<class 'tkinter.Checkbutton'>" : 0,
}

class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def set(self, x, y):
        self.x = x
        self.y = y

def resetWidgets(wi):
    for w, key in allElements.items():
                if w != wi:
                    w.config(cursor="hand2")

def resetSelectors(wis):
    for key, w in allSelectors.items():
            if key != wis:
                for s in w:
                    s.config(bg="#252d36")

def refactor_elements(w=None):
    global allElements
    if w == None:
        for widget, value in allElements.items():
            allElements[widget] = {
                "x" : widget.winfo_x() + int(widget.winfo_width() / 2),
                "y" : widget.winfo_y() + int(widget.winfo_height() / 2)
            }
    else:
        allElements[w] = {
                "x" : w.winfo_x() + int(w.winfo_width() / 2),
                "y" : w.winfo_y() + int(w.winfo_height() / 2)
            }
    

def snapToAxes(x, y, centerpoint, widget, barx, bary, hide_bar):
    snapped_x = False
    snapped_y = False
    # Snap to axes
    for w, key in allElements.items():
        if w != widget:
            xAxis = key["x"]
            yAxis = key["y"]

            if (x - 5) < xAxis and (x + 5) > xAxis:
                x = xAxis
                snapped_x = True

            if (y - 5) < yAxis and (y + 5) > yAxis:
                y = yAxis
                snapped_y = True
    
    if (x - 5) < centerpoint.x and (x + 5) > centerpoint.x:
        x = centerpoint.x
        snapped_x = True

    if (y - 5) < centerpoint.y and (y + 5) > centerpoint.y:
        y = centerpoint.y
        snapped_y = True

    # Generate guidelines
    
    if snapped_x and not hide_bar:
        #barx.place_forget()
        barx.place(y=0, x=x)
        barx.lift()
    else:
        barx.place_forget()

    if snapped_y and not hide_bar:
        #bary.place_forget()
        bary.place(y=y, x=0)
        bary.lift()
    else:
        bary.place_forget()

    return x, y

class DragManager():
    def __init__(self, widget, fun, workspace, workspaceSize):
        self.all_vars = []

        self.combobox = None
        self.root = widget
        self.selected = False
        self.fun = fun
        self.centerpoint = Vector2(int(workspaceSize.x / 2), int(workspaceSize.y / 2))
        self.workspace = workspace

        self.use_snap = True

        self.bar_x = tk.Frame(workspace, width=1, height=workspaceSize.y, bg="#f09413", name="barx")
        self.bar_y = tk.Frame(workspace, height=1, width=workspaceSize.x, bg="#13f064", name="bary")

        self.selection_box = tk.Frame(workspace, bg="#0b1a1a", name="sel")

        self.drag_offset = Vector2(0, 0)
        
        workspace.bind("<ButtonPress-1>", self.remove_selection)
    
    def set_combobox(self, box):
        self.combobox = box

    def add_var(self, wi):
        self.all_vars.append(wi)
        if self.combobox != None:
            self.combobox.config(values=self.all_vars)

    def change_settings(self, setting, var):
        self.use_snap = var

    def remove_selection(self, event):
        global selectedElement
        selectedElement = None
        resetWidgets(None)
        self.fun(None, True)
        resetSelectors(None)
        self.selection_box.place_forget()

    def align_box(self, target, state,):
        pixSize = 2
        if state == "select":
            pixSize = 1
        elif state == "drag":
            pixSize = 1

        winfo_sz = Vector2(target.winfo_width(), target.winfo_height())
        ps = Vector2(int(target.winfo_x() + (winfo_sz.x / 2)), int(target.winfo_y() + (winfo_sz.y / 2)))

        self.selection_box.config(width=winfo_sz.x + pixSize*2, height=winfo_sz.y + pixSize*2)
        self.selection_box.place_forget()
        self.selection_box.place(x=ps.x, y=ps.y, anchor=CENTER)

        self.selection_box.lower(target)

    def duplicate_selected_widget(self, func):
        global selectedElement
        if selectedElement != None:
            if selectedElement.winfo_name() != "workspace":
                oldSelected = selectedElement

                global widgetCount
                widgetCount[str(type(selectedElement))] += 1
                selectedElement = getattr(tk, str(type(selectedElement))[16:][:-2])(self.workspace, name=str(type(selectedElement))[16:][:-2].lower() + str(widgetCount[str(type(selectedElement))]))

                addFont = False
                fontBuild = {}

                for key, v in widgetArgs.items():
                    if str(type(selectedElement)) in v["types"]:
                        if v["inType"] == "config":
                            selectedElement.config(**{v["argName"] : getElementArg(oldSelected, key)})
                        if v["inType"] == "place":
                            selectedElement.place(**{v["argName"] : getElementArg(oldSelected, key)})
                        if v["inType"] == "fontc":
                            fontBuild[key] = getElementArg(oldSelected, key)
                            addFont = True
                        if v["inType"] == "img":
                            if oldSelected.cget("image") != '':
                                selectedElement.config(image=oldSelected.image_ref)
                                selectedElement.image_ref = oldSelected.image_ref

                if addFont:
                    selectedElement.config(font=(fontBuild["font-family"],fontBuild["font-size"],fontBuild["font-type"]))

                if type(selectedElement) == tk.Entry:
                    sVar = tk.StringVar()
                    sVar.set(oldSelected.var_ref.get())
                    selectedElement.var_ref = sVar
                    selectedElement.config(state="disabled", textvariable=sVar)
                    selectedElement.place(relheight=0, relwidth=0)

                selectedElement.place(anchor=CENTER, x=self.centerpoint.x, y=self.centerpoint.y)

                func(selectedElement, False)
                self.add_draggable(selectedElement, True)

                self.root.update()
                

    def remove_selected_widget(self):
        global selectedElement
        if selectedElement != None:
            if selectedElement.winfo_name() != "workspace":
                del allElements[selectedElement]

                for x in allSelectors[selectedElement]:
                    x.destroy()
                
                del allSelectors[selectedElement]

                selectedElement.destroy()
                selectedElement = None
                self.fun(None, True)
                self.selection_box.place_forget()
        
    def zindex_selected_widget(self, mode):
        if selectedElement != None:
            if mode:
                selectedElement.lift()

                self.bar_x.lift()
                self.bar_y.lift()
            else:
                selectedElement.lower()
            self.selection_box.lower(selectedElement)

    def add_draggable(self, widget, do_select):

        widget.bind("<ButtonPress-1>", self.on_start)
        widget.bind("<B1-Motion>", self.on_drag)
        widget.bind("<ButtonRelease-1>", self.on_drop)

        #allElements.append(widget)
        allElements[widget] = {}

        if do_select:
            global selectedElement
            selectedElement = widget

            widget.config(cursor="fleur")
            self.align_box(widget, "select")

            resetWidgets(widget)
            self.fun(widget, True)
        else:
            widget.config(cursor="hand2")
        
        resetSelectors(None)

        allElements[widget] = {
            "x" : widget.winfo_x() + int(widget.winfo_width() / 2),
            "y" : widget.winfo_y() + int(widget.winfo_height() / 2)
        }
    
    def destroy_workspace(self, xres, yres):
        workspaceWidgets = []

        for key, w in allSelectors.items():
            if key.winfo_name() != "workspace":
                w[0].destroy()
            else:
                workspaceWidgets = w
        
        allSelectors.clear()
        allSelectors[self.workspace] = workspaceWidgets

        for w, key in allElements.items():
            w.destroy()
        
        self.all_vars.clear()

        allElements.clear()

        self.selection_box.place_forget()

        self.selected = False
        self.centerpoint = Vector2(int(xres / 2), int(yres / 2))

        self.bar_x.config(height=yres)
        self.bar_y.config(width=xres)

        global selectedElement
        selectedElement = None

        global widgetCount
        for k in widgetCount.keys():
            widgetCount[k] = 0
        

    def add_widgetselector(self, widgets, target):
        allSelectors[target] = widgets
        
        for w in widgets:
            w.bind("<ButtonRelease-1>", lambda event:self.on_selector(target, widgets))
    
    def on_selector(self, target , widgets):
        global selectedElement
        selectedElement = target
        if target.winfo_name() != "workspace":
            target.config(cursor="fleur")
            self.align_box(target, "select")
        else:
            self.selection_box.place_forget()
        for w in widgets:
            w.config(bg="#33454a")
        resetSelectors(target)

        resetWidgets(target)
        self.fun(target, True)


    def on_start(self, event):
        global selectedElement
        if selectedElement == event.widget:
            x, y = self.root.winfo_pointerxy()
            offset_x, offset_y = self.root.winfo_rootx(), self.root.winfo_rooty()
            final_x, final_y = x - offset_x, y - offset_y 

            widget_center_x, widget_center_y = int(event.widget.winfo_x() + (event.widget.winfo_width() / 2)), int(event.widget.winfo_y() + (event.widget.winfo_height() / 2))
            
            self.drag_offset.set(final_x - widget_center_x, final_y - widget_center_y)

            self.selected = True
            self.selection_box.place_forget()
        else:
            selectedElement = event.widget
            resetWidgets(event.widget)
            self.fun(event.widget, False)
            self.align_box(event.widget, "select")
            resetSelectors(None)


    def on_drag(self, event):
        if self.selected:
            x, y = self.root.winfo_pointerxy()
            offset_x, offset_y = self.root.winfo_rootx(), self.root.winfo_rooty()
            final_x, final_y = x - offset_x - self.drag_offset.x, y - offset_y - self.drag_offset.y
            if self.use_snap:
                final_x, final_y = snapToAxes(final_x, final_y, self.centerpoint, event.widget, self.bar_x, self.bar_y, False)
            
            #event.widget.place_forget()
            event.widget.place(x=final_x, y=final_y, anchor=CENTER)
            #self.fun(event.widget, False)
            #self.align_box(event.widget, "drag", Vector2(final_x, final_y))
    
    def on_drop(self, event):
        if self.selected:
            x, y = self.root.winfo_pointerxy()
            offset_x, offset_y = self.root.winfo_rootx(), self.root.winfo_rooty()
            final_x, final_y = x - offset_x - self.drag_offset.x, y - offset_y - self.drag_offset.y
            if self.use_snap:
                final_x, final_y = snapToAxes(final_x, final_y, self.centerpoint, event.widget, self.bar_x, self.bar_y, True)

            #event.widget.place_forget()
            event.widget.place(x=final_x, y=final_y, anchor=CENTER)

            self.fun(event.widget, False)

            allElements[event.widget] = {
                "x" : final_x,
                "y" : final_y
            }
        event.widget.config(cursor="fleur")
        self.align_box(event.widget, "select")
        self.selected = False

def getElementArg(el, info):
    if info == "x":
        return el.winfo_x() + int(el.winfo_width() / 2)
    elif info == "y":
        return el.winfo_y() + int(el.winfo_height() / 2)
    elif info == "height" or info == "height-e":
        return el.winfo_height()
    elif info == "width" or info == "width-e":
        return el.winfo_width()
    elif info == "name":
        return el.winfo_name()
    elif info == "bg":
        return el.cget("bg")
    elif info == "text":
        return el.cget("text")
    elif info == "font-size":
        v = el.cget("font")
        if v[0] == "{":
            v = v[1:]
            v = v.split("}")
            return v[1].split(" ")[1]
        else:
            return el.cget("font").split(" ")[1]
    elif info == "font-family":
        v = el.cget("font")
        if v[0] == "{":
            v = v[1:]
            v = v.split("}")
            return v[0]
        else:
            return el.cget("font").split(" ")[0]
    elif info == "font-type":
        v = el.cget("font")
        if v[0] == "{":
            v = v[1:]
            v = v.split("}")
            return v[1].split(" ")[2]
        else:
            return el.cget("font").split(" ")[2]
    elif info == "fg":
        return el.cget("fg")
    elif info == "image-path":
        if el.cget("image") == '':
            return ''
        else:
            return el.image_ref.cget("file")
    elif info == "activebackground":
        return el.cget("activebackground")
    elif info == "activeforeground":
        return el.cget("activeforeground")
    elif info == "bg-de":
        return el.cget("disabledbackground")
    elif info == "fg-de":
        return el.cget("disabledforeground")
    elif info == "text-e":
        return el.var_ref.get()
    elif info == "value":
        return el.cget("value")
    elif info == "variable":
        return str(el.cget("variable"))
    elif info == "onvalue":
        return el.cget("onvalue")
    elif info == "offvalue":
        return el.cget("offvalue")


    return None

widgetArgs = {
    "name" : {
        "argName" : "name",
        "argType" : "string",
        "inType" : "None",
        "isColor" : False,
        "types" : ["<class 'tkinter.Frame'>", "<class 'tkinter.Label'>", "workspace", "<class 'tkinter.Button'>", "<class 'tkinter.LabelFrame'>", "<class 'tkinter.Entry'>", "<class 'tkinter.Radiobutton'>", "<class 'tkinter.Checkbutton'>"]
    },
    "x" : {
        "argName" : "x",
        "argType" : "int",
        "inType" : "place",
        "isColor" : False,
        "types" : ["<class 'tkinter.Frame'>", "<class 'tkinter.Label'>", "<class 'tkinter.Button'>", "<class 'tkinter.LabelFrame'>", "<class 'tkinter.Entry'>", "<class 'tkinter.Radiobutton'>", "<class 'tkinter.Checkbutton'>"]
    },
    "y" : {
        "argName" : "y",
        "argType" : "int",
        "inType" : "place",
        "isColor" : False,
        "types" : ["<class 'tkinter.Frame'>", "<class 'tkinter.Label'>", "<class 'tkinter.Button'>", "<class 'tkinter.LabelFrame'>", "<class 'tkinter.Entry'>", "<class 'tkinter.Radiobutton'>", "<class 'tkinter.Checkbutton'>"]
    },
    "width" : {
        "argName" : "width",
        "argType" : "int",
        "inType" : "config",
        "isColor" : False,
        "types" : ["<class 'tkinter.Frame'>", "<class 'tkinter.LabelFrame'>"]
    },
    "height" : {
        "argName" : "height",
        "argType" : "int",
        "inType" : "config",
        "isColor" : False,
        "types" : ["<class 'tkinter.Frame'>", "<class 'tkinter.LabelFrame'>"]
    },
    "width-e" : {
        "argName" : "width",
        "argType" : "int",
        "inType" : "place",
        "isColor" : False,
        "types" : ["<class 'tkinter.Entry'>", "<class 'tkinter.Button'>", "<class 'tkinter.Radiobutton'>", "<class 'tkinter.Checkbutton'>"]
    },
    "height-e" : {
        "argName" : "height",
        "argType" : "int",
        "inType" : "place",
        "isColor" : False,
        "types" : ["<class 'tkinter.Entry'>", "<class 'tkinter.Button'>", "<class 'tkinter.Radiobutton'>", "<class 'tkinter.Checkbutton'>"]
    },
    "bg" : {
        "argName" : "bg",
        "argType" : "string",
        "inType" : "config",
        "isColor" : True,
        "types" : ["<class 'tkinter.Frame'>", "<class 'tkinter.Label'>", "workspace", "<class 'tkinter.Button'>", "<class 'tkinter.LabelFrame'>", "<class 'tkinter.Radiobutton'>", "<class 'tkinter.Checkbutton'>"]
    },
    "activebackground" : {
        "argName" : "activebackground",
        "argType" : "string",
        "inType" : "config",
        "isColor" : True,
        "types" : ["<class 'tkinter.Button'>", "<class 'tkinter.Radiobutton'>", "<class 'tkinter.Checkbutton'>"]
    },
    "fg" : {
        "argName" : "fg",
        "argType" : "string",
        "inType" : "config",
        "isColor" : True,
        "types" : ["<class 'tkinter.Label'>", "<class 'tkinter.Button'>", "<class 'tkinter.LabelFrame'>", "<class 'tkinter.Radiobutton'>", "<class 'tkinter.Checkbutton'>"]
    },
    "activeforeground" : {
        "argName" : "activeforeground",
        "argType" : "string",
        "inType" : "config",
        "isColor" : True,
        "types" : ["<class 'tkinter.Button'>", "<class 'tkinter.Radiobutton'>", "<class 'tkinter.Checkbutton'>"]
    },
    "bg-de" : {
        "saveName" : "bg",
        "argName" : "disabledbackground",
        "argType" : "string",
        "inType" : "config",
        "isColor" : True,
        "types" : ["<class 'tkinter.Entry'>"]
    },
    "fg-de" : {
        "saveName" : "fg",
        "argName" : "disabledforeground",
        "argType" : "string",
        "inType" : "config",
        "isColor" : True,
        "types" : ["<class 'tkinter.Entry'>"]
    },
    "text" : {
        "argName" : "text",
        "argType" : "string",
        "inType" : "config",
        "isColor" : False,
        "types" : ["<class 'tkinter.Label'>", "<class 'tkinter.Button'>", "<class 'tkinter.LabelFrame'>", "<class 'tkinter.Radiobutton'>", "<class 'tkinter.Checkbutton'>"]
    },
    "text-e" : {
        "saveName" : "text",
        "argName" : "text-e",
        "argType" : "string",
        "inType" : "var",
        "isColor" : False,
        "types" : ["<class 'tkinter.Entry'>"]
    },
    "font-family" : {
        "argName" : "font-family",
        "argType" : "string",
        "inType" : "fontc",
        "isColor" : False,
        "types" : ["<class 'tkinter.Label'>", "<class 'tkinter.Button'>", "<class 'tkinter.LabelFrame'>", "<class 'tkinter.Entry'>", "<class 'tkinter.Radiobutton'>", "<class 'tkinter.Checkbutton'>"]
    },
    "font-size" : {
        "argName" : "font-size",
        "argType" : "string",
        "inType" : "fontc",
        "isColor" : False,
        "types" : ["<class 'tkinter.Label'>", "<class 'tkinter.Button'>", "<class 'tkinter.LabelFrame'>", "<class 'tkinter.Entry'>", "<class 'tkinter.Radiobutton'>", "<class 'tkinter.Checkbutton'>"]
    },
    "font-type" : {
        "argName" : "font-type",
        "argType" : "string",
        "inType" : "fontc",
        "isColor" : False,
        "types" : ["<class 'tkinter.Label'>", "<class 'tkinter.Button'>", "<class 'tkinter.LabelFrame'>", "<class 'tkinter.Entry'>", "<class 'tkinter.Radiobutton'>", "<class 'tkinter.Checkbutton'>"]
    },
    "image-path" : {
        "argName" : "image-path",
        "argType" : "string",
        "inType" : "img",
        "isColor" : False,
        "types" : ["<class 'tkinter.Label'>", "<class 'tkinter.Button'>", "<class 'tkinter.Radiobutton'>", "<class 'tkinter.Checkbutton'>"]
    },
    "value" : {
        "argName" : "value",
        "argType" : "string",
        "inType" : "config",
        "isColor" : False,
        "types" : ["<class 'tkinter.Radiobutton'>"]
    },
    "onvalue" : {
        "argName" : "onvalue",
        "argType" : "string",
        "inType" : "config",
        "isColor" : False,
        "types" : ["<class 'tkinter.Checkbutton'>"]
    },
    "offvalue" : {
        "argName" : "offvalue",
        "argType" : "string",
        "inType" : "config",
        "isColor" : False,
        "types" : ["<class 'tkinter.Checkbutton'>"]
    },
    "variable" : {
        "argName" : "variable",
        "argType" : "var",
        "inType" : "config",
        "isColor" : False,
        "types" : ["<class 'tkinter.Radiobutton'>", "<class 'tkinter.Checkbutton'>"]
    },
}