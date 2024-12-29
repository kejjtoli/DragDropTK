from tkinter import *
import tkinter as tk

selectedElement = None

allElements = {}

allSelectors = {}

class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def resetWidgets(wi):
    for w, key in allElements.items():
                if w != wi:
                    w.config(highlightthickness=0, highlightbackground="#1a1e24")

def resetSelectors(wis):
    for key, w in allSelectors.items():
            if key != wis:
                for s in w:
                    s.config(bg="#252d36")

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
        barx.place_forget()
        barx.place(y=0, x=x)
        barx.lift()
    else:
        if barx.winfo_ismapped():
            barx.place_forget()

    if snapped_y and not hide_bar:
        bary.place_forget()
        bary.place(y=y, x=0)
        bary.lift()
    else:
        if bary.winfo_ismapped():
            bary.place_forget()

    return x, y

class DragManager():
    def __init__(self, widget, fun, workspace, workspaceSize):
        self.root = widget
        self.selected = False
        self.fun = fun
        self.centerpoint = Vector2(int(workspaceSize.x / 2), int(workspaceSize.y / 2))
        self.workspace = workspace

        self.use_snap = True

        self.bar_x = tk.Frame(workspace, width=1, height=workspaceSize.y, bg="#f09413", name="barx")
        self.bar_y = tk.Frame(workspace, height=1, width=workspaceSize.x, bg="#13f064", name="bary")
        
        workspace.bind("<ButtonPress-1>", self.remove_selection)
    
    def change_settings(self, setting, var):
        self.use_snap = var

    def remove_selection(self, event):
        global selectedElement
        selectedElement = None
        resetWidgets(None)
        self.fun(None, True)
        resetSelectors(None)

    def duplicate_selected_widget(self, func):
        global selectedElement
        if selectedElement != None:
            if selectedElement.winfo_name() != "workspace":
                oldSelected = selectedElement

                
                selectedElement = getattr(tk, str(type(selectedElement))[16:][:-2])(self.workspace)

                addFont = False
                fontBuild = {}

                for key, v in widgetArgs.items():
                    if str(type(selectedElement)) in v["types"]:
                        if v["inType"] == "config":
                            selectedElement.config(**{key : getElementArg(oldSelected, key)})
                        if v["inType"] == "fontc":
                            fontBuild[key] = getElementArg(oldSelected, key)
                            addFont = True

                if addFont:
                    selectedElement.config(font=(fontBuild["font-family"],fontBuild["font-size"],fontBuild["font-type"]))

                selectedElement.place(anchor=CENTER, x=self.centerpoint.x, y=self.centerpoint.y)

                func(selectedElement, False)
                self.add_draggable(selectedElement)

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
        
    def zindex_selected_widget(self, mode):
        if selectedElement != None:
            if mode:
                selectedElement.lift()

                self.bar_x.lift()
                self.bar_y.lift()
            else:
                selectedElement.lower()

    def add_draggable(self, widget):
        global selectedElement
        selectedElement = widget

        widget.config(highlightthickness=1, highlightbackground="#1a1e24")

        widget.bind("<ButtonPress-1>", self.on_start)
        widget.bind("<B1-Motion>", self.on_drag)
        widget.bind("<ButtonRelease-1>", self.on_drop)

        #allElements.append(widget)
        allElements[widget] = {
            "x" : self.centerpoint.x,
            "y" : self.centerpoint.y
        }

        resetWidgets(widget)
        self.fun(widget, True)
        resetSelectors(None)
    
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
        
        allElements.clear()

        self.selected = False
        self.centerpoint = Vector2(int(xres / 2), int(yres / 2))

        self.bar_x.config(height=yres)
        self.bar_y.config(width=xres)

        selectedElement = None
        

    def add_widgetselector(self, widgets, target):
        allSelectors[target] = widgets
        
        for w in widgets:
            w.bind("<ButtonRelease-1>", lambda event:self.on_selector(target, widgets))
    
    def on_selector(self, target , widgets):
        global selectedElement
        selectedElement = target
        if target.winfo_name() != "workspace":
            target.config(highlightthickness=1, highlightbackground="#1a1e24")
        for w in widgets:
            w.config(bg="#33454a")
        resetSelectors(target)

        resetWidgets(target)
        self.fun(target, True)


    def on_start(self, event):
        global selectedElement
        if selectedElement == event.widget:
            self.selected = True
            event.widget.config(highlightthickness=2, highlightbackground="#1a1e24")
        else:
            selectedElement = event.widget
            resetWidgets(event.widget)
            self.fun(event.widget, False)
            event.widget.config(highlightthickness=1, highlightbackground="#1a1e24")
            resetSelectors(None)


    def on_drag(self, event):
        if self.selected:
            x, y = self.root.winfo_pointerxy()
            offset_x, offset_y = self.root.winfo_rootx(), self.root.winfo_rooty()
            final_x, final_y = x - offset_x, y - offset_y 
            if self.use_snap:
                final_x, final_y = snapToAxes(final_x, final_y, self.centerpoint, event.widget, self.bar_x, self.bar_y, False)

            event.widget.place_forget()
            event.widget.place(x=final_x, y=final_y, anchor=CENTER)
            #self.fun(event.widget, False)
    
    def on_drop(self, event):
        if self.selected:
            x, y = self.root.winfo_pointerxy()
            offset_x, offset_y = self.root.winfo_rootx(), self.root.winfo_rooty()
            final_x, final_y = x - offset_x, y - offset_y 
            if self.use_snap:
                final_x, final_y = snapToAxes(final_x, final_y, self.centerpoint, event.widget, self.bar_x, self.bar_y, True)

            event.widget.place_forget()
            event.widget.place(x=final_x, y=final_y, anchor=CENTER)

            self.fun(event.widget, False)

            allElements[event.widget] = {
                "x" : final_x,
                "y" : final_y
            }
        event.widget.config(highlightthickness=1, highlightbackground="#1a1e24")
        self.selected = False

def getElementArg(el, info):
    if info == "x":
        return el.winfo_x() + int(el.winfo_width() / 2)
    elif info == "y":
        return el.winfo_y() + int(el.winfo_height() / 2)
    elif info == "height":
        return el.winfo_height()
    elif info == "width":
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

    return None

widgetArgs = {
    "name" : {
        "argType" : "string",
        "inType" : "None",
        "types" : ["<class 'tkinter.Frame'>", "<class 'tkinter.Label'>", "workspace", "<class 'tkinter.Button'>"]
    },
    "x" : {
        "argType" : "int",
        "inType" : "place",
        "types" : ["<class 'tkinter.Frame'>", "<class 'tkinter.Label'>", "<class 'tkinter.Button'>"]
    },
    "y" : {
        "argType" : "int",
        "inType" : "place",
        "types" : ["<class 'tkinter.Frame'>", "<class 'tkinter.Label'>", "<class 'tkinter.Button'>"]
    },
    "width" : {
        "argType" : "int",
        "inType" : "config",
        "types" : ["<class 'tkinter.Frame'>"]
    },
    "height" : {
        "argType" : "int",
        "inType" : "config",
        "types" : ["<class 'tkinter.Frame'>"]
    },
    "bg" : {
        "argType" : "string",
        "inType" : "config",
        "types" : ["<class 'tkinter.Frame'>", "<class 'tkinter.Label'>", "workspace"]
    },
    "fg" : {
        "argType" : "string",
        "inType" : "config",
        "types" : ["<class 'tkinter.Label'>"]
    },
    "text" : {
        "argType" : "string",
        "inType" : "config",
        "types" : ["<class 'tkinter.Label'>", "<class 'tkinter.Button'>"]
    },
    "font-family" : {
        "argType" : "string",
        "inType" : "fontc",
        "types" : ["<class 'tkinter.Label'>", "<class 'tkinter.Button'>"]
    },
    "font-size" : {
        "argType" : "string",
        "inType" : "fontc",
        "types" : ["<class 'tkinter.Label'>", "<class 'tkinter.Button'>"]
    },
    "font-type" : {
        "argType" : "string",
        "inType" : "fontc",
        "types" : ["<class 'tkinter.Label'>", "<class 'tkinter.Button'>"]
    },
}