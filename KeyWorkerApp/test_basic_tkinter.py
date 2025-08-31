import tkinter as tk

# Test basic tkinter
root = tk.Tk()
root.title("Basic Tkinter Test")
root.geometry("300x200")

label = tk.Label(root, text="Basic Tkinter Test - Do you see this?")
label.pack(pady=50)

button = tk.Button(root, text="Click Me", command=lambda: print("Button clicked!"))
button.pack(pady=10)

root.mainloop()
