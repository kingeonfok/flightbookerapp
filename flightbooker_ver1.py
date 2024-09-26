import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

#Path for storing user credentials in JSON file
CREDENTIALS_FILE = "app_files/ver1_credentials/credentials.json"

#Main application class
class FlightBookingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        #Sets application window title and dimensions
        self.title("ForFly")
        self.geometry("800x600")
        self.center_window()
        
        self.frames = {}  #Dictionary to store different pages
        self.create_frames()
        self.show_frame("LoginPage")  #Shows the login page

    def center_window(self):
        #Centers the window
        window_width = 800
        window_height = 600
        screen_width = self.winfo_screenwidth() 
        screen_height = self.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        #Sets the geometry for the window
        self.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

    def create_frames(self):
        #Creates a container to hold pages
        container = ttk.Frame(self)
        container.pack(expand=True, fill='both')

        for F in (LoginPage, RegisterPage, HomePage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)  #Creates an instance of the frame
            self.frames[page_name] = frame  #Stores frame in the dictionary
            frame.pack()

    def show_frame(self, page_name):
        #Hide all frames
        for frame in self.frames.values():
            frame.pack_forget()
        
        #Shows the frame
        frame = self.frames[page_name]
        frame.pack(side="top", fill="both", expand=True)
        frame.tkraise()


#Login page class
class LoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        #Create the login layout
        ttk.Label(self, text="ForFly", font=("Helvetica", 24)).pack(pady=20)

        self.username = tk.StringVar()  #Variable for username input
        self.password = tk.StringVar()  #Variable for password input

        #Username input
        ttk.Label(self, text="Username:").pack(pady=5)
        ttk.Entry(self, textvariable=self.username).pack(pady=5)

        #Password input with changing to hidden characters
        ttk.Label(self, text="Password:").pack(pady=5)
        ttk.Entry(self, textvariable=self.password, show="*").pack(pady=5)

        #Buttons for login and registration page
        ttk.Button(self, text="Login", command=self.login).pack(pady=10)
        ttk.Button(self, text="Register", command=lambda: controller.show_frame("RegisterPage")).pack(pady=10)

    def login(self):
        #Gets the input username and password
        username = self.username.get()
        password = self.password.get()

        try:
            #Load the credentials from the JSON file
            with open(CREDENTIALS_FILE, "r") as f:
                credentials = json.load(f)
        except FileNotFoundError:
            #Show an error if the credentials file doesn't exist
            messagebox.showerror("Error", "No registered users found.")
            return

        #Check if the entered credentials matches
        if credentials.get(username) == password:
            self.controller.show_frame("HomePage")  #Navigate to the homepage
        else:
            messagebox.showerror("Error", "Invalid credentials.")  #Show error if incorrect


#Register page class
class RegisterPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        #Creates the registration form 
        ttk.Label(self, text="ForFly", font=("Helvetica", 24)).pack(pady=20)

        self.username = tk.StringVar()  #Variable for username input
        self.password = tk.StringVar()  #Variable for password input

        #Username input
        ttk.Label(self, text="Username:").pack(pady=5)
        ttk.Entry(self, textvariable=self.username).pack(pady=5)

        #Password input
        ttk.Label(self, text="Password:").pack(pady=5)
        ttk.Entry(self, textvariable=self.password, show="*").pack(pady=5)

        #Buttons for navigation
        ttk.Button(self, text="Register", command=self.register).pack(pady=10)
        ttk.Button(self, text="Back to Login", command=lambda: controller.show_frame("LoginPage")).pack(pady=10)

    def register(self):
        #Gets the input username and password
        username = self.username.get()
        password = self.password.get()

        os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)

        try:
            #Loads the existing credentials file
            with open(CREDENTIALS_FILE, "r") as f:
                credentials = json.load(f)
        except FileNotFoundError:
            credentials = {}

        #Checks if username already exists
        if username in credentials:
            messagebox.showerror("Error", "Username already exists.")
            return

        #Save the new credentials in file
        credentials[username] = password
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump(credentials, f)

        messagebox.showinfo("Success", "Registration successful.")  #Show success message
        self.controller.show_frame("LoginPage")


#Class for homepage
class HomePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Welcome to the ForFly Flight Booking App!", font=("Helvetica", 16)).pack(pady=20)


#Starts the application
if __name__ == "__main__":
    app = FlightBookingApp()
    app.mainloop()
