import tkinter as tk
from tkinter import *
                
root = Tk()

root.title("My Window")
root.geometry("560x400")
root.config(bg="#041012")

# Button functions

def press_button():
	print('button pressed!')

# Adding widgets

frame = tk.Frame(root, name="!frame", width=560, height=280, bg="#07191c")
frame.place(anchor=CENTER, x=280, y=217)

label = tk.Label(root, name="!label", bg="#041012", fg="white", text="Welcome to DragDropTK!", font=("Yu Gothic", "29", "bold"))
label.place(anchor=CENTER, x=280, y=40)

label2 = tk.Label(root, name="!label2", bg="#041012", fg="white", text="Made in DragDropTK!", font=("Yu Gothic", "14", "normal"))
label2.place(anchor=CENTER, x=113, y=379)

label3 = tk.Label(root, name="!label3", bg="#07191c", fg="white", text="Easy to use Tkinter based", font=("Calibri", "28", "italic"))
label3.place(anchor=CENTER, x=280, y=115)

label4 = tk.Label(root, name="!label4", bg="#07191c", fg="white", text="UI design tool!", font=("Calibri", "22", "italic"))
label4.place(anchor=CENTER, x=280, y=165)

button = tk.Button(root, name="!button", text="Free Cookie!", font=("Verdana", "20", "bold"), command=press_button)
button.place(anchor=CENTER, x=280, y=293)

label5 = tk.Label(root, name="!label5", bg="#07191c", fg="gray", text="Press this button for a free cookie!", font=("Verdana", "20", "normal"))
label5.place(anchor=CENTER, x=280, y=232)

root.mainloop()