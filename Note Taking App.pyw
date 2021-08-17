# importing all the required modules for the GUI, mysql and email
from tkinter import *
from tkinter import messagebox
from mysql import connector
from email.message import EmailMessage
import smtplib
import os

# database credentials
# db_user = os.environ.get('DB_USER')
# db_pass = os.environ.get('DB_PASS')

# creates a connection to the MySQL server
conn = connector.connect(host = "localhost", user = "root", password = "pass")
cur = conn.cursor()

# creating a database if not exists already and using it
cur.execute("create database if not exists notes_taking_app")
conn.database = "notes_taking_app"

# create table if not exists already in the database notes_taking_app
cur.execute("create table if not exists notes(note_id int auto_increment primary key, "\
            "title varchar(100) unique not null, note varchar(2000) not null)")

# callback function for the saveButton
# inserting note into database as well clearing the
# current GUI and inserting new note into the GUI
def save():
    try:
        if(title.get().rstrip() == ""):
            messagebox.showerror("ERROR!", "Please enter the title!")
            return
        cur.execute("insert into notes(title, note) value(%s, %s)", (title.get(), text.get(1.0, END)))
        conn.commit()
        notesList.insert(END, title.get())
        title.delete(0, END)
        text.delete(1.0, END)
        editButton.config(state=DISABLED)
        deleteButton.config(state=DISABLED)
        emailButton.config(state=DISABLED)
    except:
        messagebox.showerror("ERROR!", "Select a note or Title already exists!")


# callback function for clear button
# clearing the selected note and deleting the
# contents written in the title and text area
def clear():
    title.delete(0, END)
    text.delete(1.0, END)
    notesList.selection_clear(0, END)
    editButton.config(state=DISABLED)
    deleteButton.config(state=DISABLED)
    emailButton.config(state=DISABLED)

# callback function for editButton
# updating the edited content in the title and
# text area in the GUI as well as in the database
def edit():
    try:
        selectedInd = notesList.curselection()
        try:
            if (title.get() == ""):
                messagebox.showerror("ERROR!", "Please enter the title!")
                return
            selectedTitle = notesList.get(notesList.curselection())
            cur.execute(f"select note_id from notes where title = '{selectedTitle}'")
            noteId = cur.fetchone()[0]
            try:
                cur.execute(f"update notes set title = '{title.get()}', note = '{text.get(1.0, END)}' where note_id = '{noteId}'")
                conn.commit()
            except:
                messagebox.showerror("ERROR!", "Title already exists!")
                return
            notesList.delete(selectedInd)
            notesList.insert(selectedInd, title.get())
            title.delete(0, END)
            text.delete(1.0, END)
            editButton.config(state=DISABLED)
            deleteButton.config(state=DISABLED)
            emailButton.config(state=DISABLED)
        except:
            messagebox.showerror("ERROR!", "Please select a note!")
    except:
        pass


# callback function for deleteButton
# deleting the note from the GUI and
# as well as from the database
def delete():
    try:
        if(messagebox.askquestion(title = "Delete?", message = "Are you sure you want to delete the note?", icon = "warning") == "yes"):
            selectedInd = notesList.curselection()
            cur.execute(f"delete from notes where title = '{title.get()}'")
            conn.commit()
            notesList.delete(selectedInd)
            title.delete(0, END)
            text.delete(1.0, END)
            editButton.config(state=DISABLED)
            deleteButton.config(state=DISABLED)
            emailButton.config(state=DISABLED)
    except:
        messagebox.showerror("ERROR!", "Please select a note!")


# callback function for emailButton
# sending email to the reciever email address
# from the sender emiail address entered by the user
def Email():

    # sending mail
    def sendMail():
        try:
            msg = EmailMessage()
            msg.set_content(text.get(1.0, END))
            msg['Subject'] = title.get()
            msg['From'] = sender_email.get()
            msg['To'] = receiver_email.get()
            s = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            s.login(sender_email.get(), sender_email_pass.get())
            s.send_message(msg)
            s.quit()
            messagebox.showinfo("Mail Sent", "Mail Sent Successfully!")
            mailDetails.destroy()
        except Exception as e:
            messagebox.showerror("ERROR!", "Please enter a valid email address or password!")

    # GUI window to take the details of the email
    mailDetails = Toplevel(wind)
    mailDetails.wm_iconbitmap("notes.ico")
    mailDetails.geometry("500x250")
    mailDetails['background'] = "#BCD3F4"
    mailDetails.title("Email Details")
    sender_emailLabel = Label(mailDetails, text = "Your Email Address: ", background = "#1D0E83", foreground = "white")
    sender_emailLabel.grid(padx = (30, 20), pady = (30, 30))
    sender_email = Entry(mailDetails, width = 40)
    sender_email.grid(row = 0, column = 1, pady = (30, 30))
    sender_email_passLabel = Label(mailDetails, text = "Your Email Password: ", background = "#1D0E83", foreground = "white")
    sender_email_passLabel.grid(row = 1, column = 0, padx = (30, 20), pady = (0, 30))
    sender_email_pass = Entry(mailDetails, show = '*', width = 40)
    sender_email_pass.grid(row = 1, column = 1, pady = (0, 30))
    receiver_emailLabel = Label(mailDetails, text = "Receiver's Email Address: ", background = "#1D0E83", foreground = "white")
    receiver_emailLabel.grid(row = 2, column = 0, pady = (0, 30), padx = (30, 20),)
    receiver_email = Entry(mailDetails, width = 40)
    receiver_email.grid(row = 2, column = 1,  pady = (0, 30))
    send_button = Button(mailDetails, text = "Send", command = sendMail, background = "#1D0E83", foreground = "white")
    send_button.grid(row = 3, column = 1)


# call back function for search button
# searching the note and displaying it onto the GUI
# which is entered by the user in the entry field
def search():
    title.delete(0, END)
    text.delete(1.0, END)
    if notesSearch.get() == "":
        messagebox.showinfo(title = "Empty", message = "Please enter note title to search!")
        return
    cur.execute(f"select title from notes where title LIKE '{notesSearch.get()}%'")
    notesList.delete(0, END)
    titles = cur.fetchall()
    if (cur.rowcount == 0):
        messagebox.showinfo(title="Not Found", message="Searched note not exist")
        return
    for i in titles:
        notesList.insert(END, i)


# call back function for cancel button
# clearing the notes which are searched previously
# and displaying all the saved notes
def cancel():
    notesSearch.delete(0, END)
    notesList.delete(0, END)
    title.delete(0, END)
    text.delete(1.0, END)
    showAllLists()


# Select and Display the selected note from the listbox
def selectedNote(event):
    editButton.config(state=NORMAL)
    deleteButton.config(state=NORMAL)
    emailButton.config(state=NORMAL)
    try:
        selectedNote = notesList.get(notesList.curselection())
        if type(selectedNote) == tuple:
            selectedNote = str(selectedNote[0])
        title.delete(0, END)
        text.delete('1.0', END)
        cur.execute(f"select title, note from notes where title = '{selectedNote}'")
        note = cur.fetchone()
        title.insert(END, note[0])
        text.insert(END, note[1])
    except Exception as e:
        pass


# Show all the saved notes title in the listbox
def showAllLists():
    cur.execute("select * from notes")
    notes = cur.fetchall()
    for note in notes:
        notesList.insert(END, note[1])


# Creating GUI Window
wind = Tk(className = " Note Taking App")
wind.wm_iconbitmap("Images\\notes.ico")
wind['pady'] = 3
wind['padx'] = 3
wind['borderwidth'] = 3
wind['background'] = "black"
wind.state("zoomed")

# Left frame to display saved notes and Right frame to write the notes
left_frame = Frame(wind, background = "#efe5fd", width = 400)
left_frame.pack(side = "left", fill = BOTH)
left_frame.pack_propagate(0)
right_frame = Frame(wind, background = "#efe5fd")
right_frame.pack(side = "right", expand = True, fill = BOTH)

# font style
font = ("Cambria", 14, "bold")
font1 = ("Calibri", 12)
font2 = ("Cambria", 12, "bold")

# Adding Label, Listbox and Scrollbar widgets to the left frame
notesSearchLabel = Label(left_frame, text = "Search Note", background = "#efe5fd", foreground = "#6002ee", font = font)
notesSearchLabel.place(x = 10, y = 10)
notesSearch = Entry(left_frame, font = font1)
notesSearch.pack(side = "top", fill = BOTH, padx = (10, 10), pady = (40, 10))
buttonFrame = Frame(left_frame, background = "#efe5fd")
buttonFrame.pack(side = TOP)
searchButton = Button(buttonFrame, command = search, borderwidth = 3, font = font2, text = "Search", background = "#9965f4", foreground = "white")
searchButton.pack(side = LEFT, padx = (0, 10), pady = (0, 20))
canelButton = Button(buttonFrame, command = cancel, borderwidth = 3, font = font2, text = "Cancel", background = "#9965f4", foreground = "white")
canelButton.pack(side = LEFT, padx = (10, 0), pady = (0, 20))
notesListLabel = Label(left_frame, text = "Saved Notes", background = "#efe5fd", foreground = "#6002ee", font = font)
notesListLabel.place(x = 10, y = 125)
notesList = Listbox(left_frame, cursor = "hand2", font = font1, activestyle = 'none', selectforeground = "white", selectbackground = "#6002ee")
notesList.pack(fill = BOTH, expand = True, padx = (10, 10), pady = (30, 10))
noteScrollBar = Scrollbar(notesList)
noteScrollBar.pack(side = RIGHT, fill = Y)
noteScrollBar.config(command = notesList.yview, cursor = "hand2")
notesList.config(yscrollcommand = noteScrollBar.set)
noteScrollBar1 = Scrollbar(notesList, orient = "horizontal")
noteScrollBar1.pack(side = BOTTOM, fill = X)
noteScrollBar1.config(command = notesList.xview, cursor = "hand2")
notesList.config(xscrollcommand = noteScrollBar1.set)

# to add a line between left and right frame
line = Frame(wind, width = 3, background = "black")
line.pack(side = "left", fill = Y)

# Adding Entry, Text, Scrollbars and Buttons to the right window
titleLabel = Label(right_frame, text = "Title", background = "#efe5fd", foreground = "#6002ee", font = font)
titleLabel.pack(pady = (10, 10))
title = Entry(right_frame, font = font1)
title.pack(fill = BOTH, padx = (10, 10), pady = (10, 10))
textLabel = Label(right_frame, text = "Note", background = "#efe5fd", foreground = "#6002ee", font = font)
textLabel.pack(pady = (10, 10))
text = Text(right_frame, font = font1, undo = True)
text.pack(fill = BOTH, expand = True, padx = (10, 10), pady = (10, 10))
textScrollBar = Scrollbar(text)
textScrollBar.pack(side = RIGHT, fill = Y)
textScrollBar.config(command = text.yview, cursor = "hand2")
text.config(yscrollcommand = textScrollBar.set)

# binding to the event generator
notesList.bind("<<ListboxSelect>>", selectedNote)

# Buttons
buttonFrame1 = Frame(right_frame, background = "#efe5fd")
buttonFrame1.pack(side = TOP)

save_image = PhotoImage(file = "Images\save.png")
saveButton = Button(buttonFrame1, command = save,image = save_image, borderwidth = 3, text = "Save", font = font2, compound  = TOP, width = 70, height = 75, background = "#9965f4", foreground = "white")
saveButton.pack(side = LEFT, padx = (0, 10), pady = (10, 10))

clear_image = PhotoImage(file = "Images\clear.png")
clearButton = Button(buttonFrame1, command = clear,image = clear_image, borderwidth = 3, text = "Clear", font = font2, compound  = TOP, width = 70, height = 75, background = "#9965f4", foreground = "white")
clearButton.pack(side = LEFT, padx = (0, 10), pady = (10, 10))

edit_image = PhotoImage(file = "Images\edit.png")
editButton = Button(buttonFrame1, command = edit,image = edit_image, borderwidth = 3, text = "Edit", font = font2, compound  = TOP, width = 70, height = 75, state = DISABLED, background = "#9965f4", foreground = "white")
editButton.pack(side = LEFT, padx = (0, 10), pady = (10, 10))

delete_image = PhotoImage(file = "Images\delete.png")
deleteButton = Button(buttonFrame1, command = delete,image = delete_image, borderwidth = 3, text = "Delete", font = font2, compound  = TOP, width = 70, height = 75, state = DISABLED, background = "#9965f4", foreground = "white")
deleteButton.pack(side = LEFT, padx = (0, 10), pady = (10, 10))

email_image = PhotoImage(file = "Images\email.png")
emailButton = Button(buttonFrame1, command = Email, borderwidth = 3, image = email_image, text = "Send Mail", font = font2, compound  = TOP, width = 70, height = 75, state = DISABLED, background = "#9965f4", foreground = "white")
emailButton.pack(side = LEFT, padx = (0, 10), pady = (10, 10))

# Show all saved notes
showAllLists()

# Running the GUI window
wind.mainloop()


