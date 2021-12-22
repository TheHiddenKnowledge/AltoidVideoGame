from tkinter import *
from tkinter.filedialog import askopenfilename

master = Tk(className="Game Maker")

# Strings for the chosen files
filename = ""
filenamed = "No file chosen"
# String and timer for GUI updates
updatename = ""
updatetimer = 0
# Boolean that determines if a sprite set has been saved 
saved = 0
# Container for the pixels 
widgets = []
# Container for the color selector of each pixel 
counters = []
# Indexes for the current sprite set and sprite
sprite_index = 0
set_index = 0
# Container for current sprite data 
current_sprite = []
# Container for current sprite set data 
sprites_list = []
# Container for all sprite set data 
sprite_set_list = []
# Container for number of sprites in each set 
sprite_count = [1]
# Current behavior for the sprite set 
set_behavior = []
# Number of sprite sets 
set_count = 0
# List of all possible colors that each pixel can choose from 
colors = ["black", "white", "blue", "red", "green", "cyan", "magenta", "yellow"]


# Function to change to either the previous or next sprite in a set (if available)
# The change parameter will be -1 or 1 denoting the change in the sprite index
def change_sprite(change):
    global sprite_index
    global current_sprite
    global updatename
    if saved == 1:
        # The sprite will only change if there is a sprite at the changed index
        sprite_index += change
        if sprite_index < 0:
            sprite_index -= change
        else:
            if sprite_index + 1 <= len(sprites_list):
                for i in range(len(current_sprite)):
                    current_sprite[i] = sprites_list[sprite_index][i]
            else:
                sprite_index -= change
        # Resets the counters and pixels to match the changed sprite
        for i in range(len(current_sprite)):
            counters[i] = colors.index(current_sprite[i])
            widgets[i].config(bg=current_sprite[i])
    else:
        updatename = "Sprite Set not Saved!"


# Function that adds a sprite to the current set
def add_sprite():
    global sprite_index
    global updatename
    # Resets the pixel map to have all black pixels and increases the sprite index by 1
    if saved == 1:
        for i in range(len(current_sprite)):
            current_sprite[i] = "black"
            counters[i] = 0
            widgets[i].config(bg="black")
        sprite_index += 1
    else:
        updatename = "Sprite Set not Saved!"


# Function to change to either the previous or next set (if available)
# The change parameter will be -1 or 1 denoting the change in the set index
def change_set(change):
    global set_index
    global current_sprite
    global sprite_index
    global sprites_list
    global joyv
    global followv
    global TT
    global X_coor
    global Y_coor
    global updatename
    if saved == 1:
        set_index += change
        sprite_index = 0
        # The set will only change if there is another set at the desired index
        if set_index < 0:
            set_index -= change
        else:
            if set_index + 1 <= len(sprite_set_list):
                sprites_list = sprite_set_list[set_index].copy()
                current_sprite = sprites_list[0].copy()
            else:
                set_index -= change
        # Sets the counters and pixels to match the first sprite in the changed set
        for i in range(len(current_sprite)):
            counters[i] = colors.index(current_sprite[i])
            widgets[i].config(bg=current_sprite[i])
        # Assigns the widgets for the set behavior to match the changed set
        joyv.set(set_behavior[set_index][0])
        followv.set(set_behavior[set_index][1])
        TT.delete(0, 'end')
        TT.insert(0, set_behavior[set_index][2])
        X_coor.delete(0, 'end')
        X_coor.insert(0, set_behavior[set_index][3])
        Y_coor.delete(0, 'end')
        Y_coor.insert(0, set_behavior[set_index][4])
    else:
        updatename = "Sprite Set not Saved!"


# Function to add a sprite set
def add_set():
    global set_index
    global sprite_index
    global updatename
    # Resets the pixel map to have all black pixels and increases the set index by 1
    if saved == 1:
        del sprites_list[:]
        for i in range(len(current_sprite)):
            current_sprite[i] = "black"
            counters[i] = 0
            widgets[i].config(bg="black")
        set_index += 1
        sprite_index = 0
    else:
        updatename = "Sprite Set not Saved!"


# Function to save a sprite to the current set
def save_sprite():
    # If not a new sprite it overwrites the old data, else it adds the sprite data
    if sprite_index + 1 <= len(sprites_list):
        sprites_list[sprite_index] = current_sprite.copy()
    else:
        sprites_list.append(current_sprite.copy())


# Function to save the current set
def save_set():
    global updatename
    global set_count
    global saved
    # First save the current sprite
    save_sprite()
    # Get the components initial conditions
    tv = TT.get()
    xv = X_coor.get()
    yv = Y_coor.get()
    # Format for the initial conditions is such that anything with one digit must have a leading zero
    if int(tv) < 10:
        tv = "0" + str(int(tv))
    if int(xv) < 10:
        xv = "0" + str(int(xv))
    if int(yv) < 10:
        yv = "0" + str(int(yv))
    # If data for the current set already exists it will overwrite the data, else add the data
    if set_index + 1 <= len(sprite_set_list):
        sprite_set_list[set_index] = sprites_list.copy()
        set_behavior[set_index] = [joyv.get(), followv.get(), tv, xv, yv]
    else:
        set_count += 1
        sprite_set_list.append(sprites_list.copy())
        set_behavior.append([joyv.get(), followv.get(), tv, xv, yv])
    saved = 1
    updatename = "Set Saved!"


# Function for choosing which text file to save the set data to
def choose_file():
    global filename
    global filenamed
    filename = askopenfilename()
    filenamed = filename.split("/")[-1]


# Function for changing the color of a pixel
def change_color(index):
    global saved
    counters[index] += 1
    # Resets the color selector when it reaches the end of the list
    if counters[index] == len(colors):
        counters[index] = 0
    # Changes the container and pixel widget colors
    widgets[index].config(bg=colors[counters[index]])
    current_sprite[index] = colors[counters[index]]
    saved = 0


# Function for uploaded the set data to the chosen text file
def upload_code():
    global updatename
    if filename != "":
        # Container for lines of data to be written
        final = []
        sprite = ""
        for i in range(set_count):
            # '!' will initialize a game component
            initial = ""
            initial += "!"
            # '#' defines joystick movement
            if set_behavior[i][0] == 1:
                initial += "#"
            # '$' defines target follow movement
            if set_behavior[i][1] == 1:
                initial += "$"
            # The initial conditions for the game component
            for l in range(3):
                initial += str(set_behavior[i][2 + l])
            initial += "\n"
            final.append(initial)
            # For each sprite in the current sprite create a string that is encoded with the pixel colors
            for j in range(len(sprite_set_list[i])):
                for k in range(len(sprite_set_list[i][j])):
                    if sprite_set_list[i][j][k] == "black":
                        sprite += "b"
                    if sprite_set_list[i][j][k] == "white":
                        sprite += "w"
                    if sprite_set_list[i][j][k] == "blue":
                        sprite += "B"
                    if sprite_set_list[i][j][k] == "red":
                        sprite += "r"
                    if sprite_set_list[i][j][k] == "cyan":
                        sprite += "c"
                    if sprite_set_list[i][j][k] == "green":
                        sprite += "g"
                    if sprite_set_list[i][j][k] == "magenta":
                        sprite += "m"
                    if sprite_set_list[i][j][k] == "yellow":
                        sprite += "y"
                final.append(sprite + "\n")
                sprite = ""
        # Finally, write the formatted code to the text file
        myfile = open(filename, "w")
        myfile.writelines(final)
        myfile.close()
        updatename = "File Uploaded!"
    else:
        updatename = "No File Chosen!"


# Function for loading set data from the chosen text file
def load_code():
    global updatename
    global sprite_set_list
    global set_behavior
    global set_index
    global saved
    if filename != "":
        newObj = -1
        oldObj = -1
        temp_sprite_list = []
        myfile = open(filename, "r")
        for line in myfile:
            temp = line
            temp_behavior = []
            temp_sprite = []
            # '!' will create a new set
            if temp[0] == "!":
                newObj += 1
                # Defining the set behavior based on the entries of '#' and '$'
                if temp[1] == "#":
                    temp_behavior.append(1)
                else:
                    temp_behavior.append(0)
                if temp[1] == "$":
                    temp_behavior.append(1)
                else:
                    temp_behavior.append(0)
                # Defining the set's initial conditions
                temp_behavior.append(temp[2] + temp[3])
                temp_behavior.append(temp[4] + temp[5])
                temp_behavior.append(temp[6] + temp[7])
                set_behavior.append(temp_behavior)
                if newObj > 0:
                    sprite_set_list.append(temp_sprite_list)
                    temp_sprite_list = []
            # Reads the encoded pixel data for the current line
            if oldObj == newObj:
                for item in range(len(temp)):
                    if temp[item] == "b":
                        temp_sprite.append("black")
                    if temp[item] == "w":
                        temp_sprite.append("white")
                    if temp[item] == "B":
                        temp_sprite.append("blue")
                    if temp[item] == "r":
                        temp_sprite.append("red")
                    if temp[item] == "c":
                        temp_sprite.append("cyan")
                    if temp[item] == "g":
                        temp_sprite.append("green")
                    if temp[item] == "m":
                        temp_sprite.append("magenta")
                    if temp[item] == "y":
                        temp_sprite.append("yellow")
                temp_sprite_list.append(temp_sprite)
            oldObj = newObj
        myfile.close()
        sprite_set_list.append(temp_sprite_list)
        saved = 1
        set_index = 0
        change_set(0)
    else:
        updatename = "No File Chosen!"


def GUI_init():
    global COUNTS
    global UPDATE
    global File
    global joyv
    global followv
    global TT
    global X_coor
    global Y_coor
    # Frames
    sprite_frame = Frame(master)
    sprite_frame.grid(row=1, column=0)
    button_frame = Frame(master)
    button_frame.grid(row=1, column=1)
    behavior_frame = Frame(master)
    behavior_frame.grid(row=1, column=2)
    # Initializing pixel buttons
    for i in range(5):
        for j in range(5):
            counters.append(0)
            current_sprite.append("black")
            widgets.append(
                Button(sprite_frame, command=lambda i=i, j=j: change_color(5 * i + j), bg="black", height=2, width=5))
            widgets[5 * i + j].grid(row=i, column=j)
    # Sprite controls
    UPDATE = Label(master)
    UPDATE.grid(row=0, column=0, sticky="ew")
    COUNTS = Label(master, text="Set = " + str(set_index) + ", Sprite = " + str(sprite_index))
    COUNTS.grid(row=0, column=2, sticky="ew")
    L1 = Label(button_frame, text="Sprite Controls")
    L1.grid(row=0, column=0, columnspan=2, sticky="ew")
    Previous = Button(button_frame, command=lambda: change_sprite(-1), text="Previous Sprite")
    Previous.grid(row=1, column=0, sticky="ew")
    Next = Button(button_frame, command=lambda: change_sprite(1), text="Next Sprite")
    Next.grid(row=1, column=1, sticky="ew")
    Create = Button(button_frame, command=add_sprite, text="Add Sprite")
    Create.grid(row=2, column=0, sticky="ew")
    # Set controls
    L2 = Label(button_frame, text="Sprite Controls")
    L2.grid(row=3, column=0, columnspan=2, sticky="ew")
    Previous_set = Button(button_frame, command=lambda: change_set(-1), text="Previous Set")
    Previous_set.grid(row=4, column=0, sticky="ew")
    Next_set = Button(button_frame, command=lambda: change_set(1), text="Next Set")
    Next_set.grid(row=4, column=1, sticky="ew")
    Create_set = Button(button_frame, command=add_set, text="Add Set")
    Create_set.grid(row=5, column=0, sticky="ew")
    Save_set = Button(button_frame, command=save_set, text="Save set")
    Save_set.grid(row=5, column=1, sticky="ew")
    # Behavior controls
    joyv = BooleanVar()
    followv = BooleanVar()
    L3 = Label(behavior_frame, text="Behavior Controls")
    L3.grid(row=0, column=0, columnspan=2, sticky="ew")
    Joy = Checkbutton(behavior_frame, text="Joystick", variable=joyv)
    Joy.grid(row=1, column=0, sticky="ew")
    Follow = Checkbutton(behavior_frame, text="Follow", variable=followv)
    Follow.grid(row=1, column=1, sticky="ew")
    TT = Entry(behavior_frame)
    TT.grid(row=2, column=0, columnspan=2, sticky="ew")
    TT.insert(0, "1")
    X_coor = Entry(behavior_frame, width=10)
    X_coor.grid(row=3, column=0, sticky="ew")
    X_coor.insert(0, "0")
    Y_coor = Entry(behavior_frame, width=10)
    Y_coor.grid(row=3, column=1, sticky="ew")
    Y_coor.insert(0, "0")
    # File elements
    Open = Button(button_frame, command=choose_file, text="Choose File")
    Open.grid(row=6, column=0, sticky="ew")
    File = Label(button_frame, text="No file chosen")
    File.grid(row=6, column=1, sticky="ew")
    Upload = Button(button_frame, command=upload_code, text="Upload Code")
    Upload.grid(row=7, column=0, sticky="ew")
    Load = Button(button_frame, command=load_code, text="Load Code")
    Load.grid(row=7, column=1, sticky="ew")


def GUI_update():
    global updatename
    global updatetimer
    # Updates the set and sprite indexes
    COUNTS.configure(text="Set = " + str(set_index) + ", Sprite = " + str(sprite_index))
    # This will display various pop up messages to the user
    UPDATE.configure(text=updatename)
    if updatename != "":
        updatetimer += 1
        if updatetimer % 10 == 0:
            UPDATE.configure(font=('TkDefaultFont', 10, 'bold'))
        if updatetimer % 20 == 0:
            UPDATE.configure(font=('TkDefaultFont', 10, 'roman'))
        if updatetimer > 100:
            updatetimer = 0
            updatename = ""
    File.config(text=filenamed)
    master.after(10, GUI_update)


GUI_init()
master.after(10, GUI_update)
mainloop()
