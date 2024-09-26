import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

CREDENTIALS_FILE = "app_files/ver2_credentials/credentials.json"
FLIGHTS_FILE = "app_files/flights.json"

class FlightBookingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ForFly")
        self.geometry("800x600")
        self.center_window()
        
        self.frames = {}
        self.create_frames()
        self.show_frame("LoginPage")

    def center_window(self):
        window_width = 800
        window_height = 600
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

    def create_frames(self):
        container = ttk.Frame(self)
        container.pack(expand=True, fill='both')

        for F in (LoginPage, RegisterPage, HomePage, SearchFlightsPage, BookingPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.pack()

    def show_frame(self, page_name):
        # Hide all frames
        for frame in self.frames.values():
            frame.pack_forget()
        
        # Show the requested frame
        frame = self.frames[page_name]
        frame.pack(side="top", fill="both", expand=True)
        frame.tkraise()

class LoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="ForFly", font=("Helvetica", 24)).pack(pady=20)

        self.username = tk.StringVar()
        self.password = tk.StringVar()

        ttk.Label(self, text="Username:").pack(pady=5)
        ttk.Entry(self, textvariable=self.username).pack(pady=5)

        ttk.Label(self, text="Password:").pack(pady=5)
        ttk.Entry(self, textvariable=self.password, show="*").pack(pady=5)

        ttk.Button(self, text="Login", command=self.login).pack(pady=10)
        ttk.Button(self, text="Register", command=lambda: controller.show_frame("RegisterPage")).pack(pady=10)

    def login(self):
        username = self.username.get()
        password = self.password.get()

        try:
            with open(CREDENTIALS_FILE, "r") as f:
                credentials = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "No registered users found.")
            return

        if credentials.get(username) == password:
            self.controller.show_frame("HomePage")
        else:
            messagebox.showerror("Error", "Invalid credentials.")

class RegisterPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="ForFly", font=("Helvetica", 24)).pack(pady=20)

        self.username = tk.StringVar()
        self.password = tk.StringVar()

        ttk.Label(self, text="Username:").pack(pady=5)
        ttk.Entry(self, textvariable=self.username).pack(pady=5)

        ttk.Label(self, text="Password:").pack(pady=5)
        ttk.Entry(self, textvariable=self.password, show="*").pack(pady=5)

        ttk.Button(self, text="Register", command=self.register).pack(pady=10)
        ttk.Button(self, text="Back to Login", command=lambda: controller.show_frame("LoginPage")).pack(pady=10)

    def register(self):
        username = self.username.get()
        password = self.password.get()

        os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)

        try:
            with open(CREDENTIALS_FILE, "r") as f:
                credentials = json.load(f)
        except FileNotFoundError:
            credentials = {}

        if username in credentials:
            messagebox.showerror("Error", "Username already exists.")
            return

        credentials[username] = password
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump(credentials, f)

        messagebox.showinfo("Success", "Registration successful.")
        self.controller.show_frame("LoginPage")

class HomePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Welcome to the ForFly Flight Booking App!", font=("Helvetica", 16)).pack(pady=20)
        ttk.Button(self, text="Search Flights", command=lambda: controller.show_frame("SearchFlightsPage")).pack(pady=10)

class SearchFlightsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Search Flights", font=("Helvetica", 16)).pack(pady=20)

        ttk.Label(self, text="From:").pack(pady=5)
        self.from_entry = ttk.Entry(self)
        self.from_entry.pack(pady=5)

        ttk.Label(self, text="To:").pack(pady=5)
        self.to_entry = ttk.Entry(self)
        self.to_entry.pack(pady=5)

        ttk.Button(self, text="Search", command=self.search_flights).pack(pady=10)

        self.results_frame = ttk.Frame(self)
        self.results_frame.pack(pady=10)

    def search_flights(self):
        from_location = self.from_entry.get()
        to_location = self.to_entry.get()

        try:
            with open(FLIGHTS_FILE, "r") as f:
                flights = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "No flights data found.")
            return

        matching_flights = [
            flight for flight in flights if
            flight.get("origin") == from_location and
            flight.get("destination") == to_location
        ]

        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if matching_flights:
            for flight in matching_flights:
                flight_info = f"{flight['origin']} to {flight['destination']} - Flight Number: {flight['flight_number']} - Price: ${flight['price']}"
                ttk.Button(self.results_frame, text=flight_info, command=lambda f=flight: self.select_flight(f)).pack(pady=5)
        else:
            ttk.Label(self.results_frame, text="No flights found.").pack(pady=5)

    def select_flight(self, flight):
        self.controller.show_frame("BookingPage")

class BookingPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Confirm Booking", font=("Helvetica", 16)).pack(pady=20)
        ttk.Button(self, text="Back to Home", command=lambda: controller.show_frame("HomePage")).pack(pady=10)

if __name__ == "__main__":
    app = FlightBookingApp()
    app.mainloop()
