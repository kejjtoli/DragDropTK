import tkinter as tk
from tkinter import *
                
root = Tk()

root.title("My Window")
root.geometry("500x400")
root.config(bg="#051414")

# Button functions

def press_button2():
	print('button2 pressed!')

# Adding widgets

frame2 = tk.Frame(root, name="!frame2", width=560, height=280, bg="#0b2121")
frame2.place(anchor=CENTER, x=250, y=215)

label = tk.Label(root, name="!label", bg="#051414", fg="#edf0f0", text="Welcome to DragDropTK!", font=("Corbel", "30", "bold"))
label.place(anchor=CENTER, x=250, y=37)

label2 = tk.Label(root, name="!label2", bg="#0b2121", fg="#edf0f0", text="Easy to use Tkinter based", font=("Calibri", "26", "italic"))
label2.place(anchor=CENTER, x=250, y=103)

label3 = tk.Label(root, name="!label3", bg="#0b2121", fg="#edf0f0", text="UI design tool", font=("Calibri", "22", "italic"))
label3.place(anchor=CENTER, x=250, y=141)

label4 = tk.Label(root, name="!label4", bg="#051414", fg="#edf0f0", text="Made in DragDropTK", font=("Corbel", "15", "normal"))
label4.place(anchor=CENTER, x=100, y=378)

label6 = tk.Label(root, name="!label6", bg="#0b2121", fg="#878a8a", text="Press button for a free cookie!", font=("Calibri", "24", "normal"))
label6.place(anchor=CENTER, x=250, y=208)

button2 = tk.Button(root, name="!button2", text="Free Cookie", font=("Corbel", "22", "bold"), command=press_button2)
button2.place(anchor=CENTER, x=250, y=275)

root.mainloop()