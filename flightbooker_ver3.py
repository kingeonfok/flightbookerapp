import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from PIL import Image, ImageTk

#Constants for file paths
CREDENTIALS_FILE = "app_files/ver3_credentials/credentials.json"
FLIGHTS_FILE = "app_files/flights.json"

# Main application class
class FlightBookingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ForFly")
        self.geometry("800x600")
        self.center_window()
        
        self.frames = {}
        self.create_frames()
        self.show_frame("LoginPage")

    #Centers the application
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

        #Initialize and store each page in the frames dictionary
        for F in (LoginPage, RegisterPage, HomePage, SearchFlightsPage, BookingPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.pack()

    def show_frame(self, page_name):
        for frame in self.frames.values():
            frame.pack_forget()
        
        frame = self.frames[page_name]
        frame.pack(side="top", fill="both", expand=True)
        frame.tkraise()

#Login page class
class LoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="ForFly", font=("Helvetica", 24)).pack(pady=20)

        #Username and password entry fields
        self.username = tk.StringVar()
        self.password = tk.StringVar()

        ttk.Label(self, text="Username:").pack(pady=5)
        ttk.Entry(self, textvariable=self.username).pack(pady=5)

        ttk.Label(self, text="Password:").pack(pady=5)
        ttk.Entry(self, textvariable=self.password, show="*").pack(pady=5)

        #Login and register buttons
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

        #Check if the username exists and the password matches
        if credentials.get(username) == password:
            self.controller.show_frame("HomePage")
        else:
            messagebox.showerror("Error", "Invalid credentials.")

#Register page class
class RegisterPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="ForFly", font=("Helvetica", 24)).pack(pady=20)

        #Username and password entry fields
        self.username = tk.StringVar()
        self.password = tk.StringVar()

        ttk.Label(self, text="Username:").pack(pady=5)
        ttk.Entry(self, textvariable=self.username).pack(pady=5)

        ttk.Label(self, text="Password:").pack(pady=5)
        ttk.Entry(self, textvariable=self.password, show="*").pack(pady=5)

        #Register and back to login buttons
        ttk.Button(self, text="Register", command=self.register).pack(pady=10)
        ttk.Button(self, text="Back to Login", command=lambda: controller.show_frame("LoginPage")).pack(pady=10)

    def register(self):
        username = self.username.get()
        password = self.password.get()

        #Create the directory for the credentials file if it doesn't exist
        os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)

        try:
            with open(CREDENTIALS_FILE, "r") as f:
                credentials = json.load(f)
        except FileNotFoundError:
            credentials = {}

        #Checks if the username already exists
        if username in credentials:
            messagebox.showerror("Error", "Username already exists.")
            return

        #Saves new credentials
        credentials[username] = password
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump(credentials, f)

        messagebox.showinfo("Success", "Registration successful.")
        self.controller.show_frame("LoginPage")

#Home page class
class HomePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        #Welcome text and button to search flights
        ttk.Label(self, text="Welcome to the ForFly Flight Booking App!", font=("Helvetica", 16)).pack(pady=20)
        ttk.Button(self, text="Search Flights", command=lambda: controller.show_frame("SearchFlightsPage")).pack(pady=10)

#Search flights page class
class SearchFlightsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        #Labels and comboboxes for entering flight searches
        ttk.Label(self, text="Search Flights", font=("Helvetica", 16)).pack(pady=20)

        ttk.Label(self, text="From:").pack(pady=5)
        self.from_combobox = ttk.Combobox(self)
        self.from_combobox.pack(pady=5)

        ttk.Label(self, text="To:").pack(pady=5)
        self.to_combobox = ttk.Combobox(self)
        self.to_combobox.pack(pady=5)

        ttk.Button(self, text="Search", command=self.search_flights).pack(pady=10)

        self.results_frame = ttk.Frame(self)
        self.results_frame.pack(pady=10)

        self.load_locations()

    #Loads flight locations from the flights file
    def load_locations(self):
        try:
            with open(FLIGHTS_FILE, "r") as f:
                flights = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "No flights data found.")
            return

        locations = sorted(set(flight["origin"] for flight in flights) | set(flight["destination"] for flight in flights))
        self.from_combobox['values'] = locations
        self.to_combobox['values'] = locations

    #Perform search for matching flights
    def search_flights(self):
        from_location = self.from_combobox.get()
        to_location = self.to_combobox.get()

        try:
            with open(FLIGHTS_FILE, "r") as f:
                flights = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "No flights data found.")
            return

        #Filter flights based on the selected origin and destination
        matching_flights = [
            flight for flight in flights if
            flight.get("origin") == from_location and
            flight.get("destination") == to_location
        ]

        #Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        #Display matching flights or show no results message
        if matching_flights:
            for flight in matching_flights:
                flight_frame = ttk.Frame(self.results_frame)
                flight_frame.pack(pady=5)

                #Buttons to select the flight
                select_button = ttk.Button(flight_frame, text=f"Flight {flight['flight_number']} - from ${flight['price']:.2f}",
                                           command=lambda f=flight: self.select_flight(f))
                select_button.pack(side=tk.LEFT, padx=10)

                #Creates a label to display the flight details
                details_label = ttk.Label(flight_frame, text=f"Departure: {flight['departure_time']} | "
                                                             f"Arrival: {flight['arrival_time']} | "
                                                             f"Aircraft: {flight['aircraft_model']}")
                details_label.pack(side=tk.LEFT, padx=10)

        else:
            #No flights found message
            ttk.Label(self.results_frame, text="No flights found.").pack(pady=5)

    def select_flight(self, flight):
        self.controller.selected_flight = flight
        self.controller.show_frame("BookingPage")

#Booking page class
class BookingPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Confirm Booking", font=("Helvetica", 16)).pack(pady=20)

        #Entry for the passenger name
        ttk.Label(self, text="Name:").pack(pady=5)
        self.name_entry = ttk.Entry(self)
        self.name_entry.pack(pady=5)

        #Entry for the passenger age
        ttk.Label(self, text="Age:").pack(pady=5)
        self.age_entry = ttk.Entry(self)
        self.age_entry.pack(pady=5)

        ttk.Button(self, text="Confirm Booking", command=self.confirm_booking).pack(pady=10)
        ttk.Button(self, text="Back", command=lambda: self.controller.show_frame("BookingPage")).pack(pady=10)

    def confirm_booking(self):
        name = self.name_entry.get()
        age = self.age_entry.get()

        #Checks if both name and age are provided
        if not name or not age:
            messagebox.showerror("Error", "Please enter both name and age.")
            return

        #Retrieve the selected flight from the controller
        flight = self.controller.selected_flight
        if not flight:
            messagebox.showerror("Error", "No flight selected.")
            return

        #Create a summary of the booking details
        summary = (
            f"Name: {name}\n"
            f"Age: {age}\n\n"
            f"Flight Details:\n"
            f"Flight Number: {flight['flight_number']}\n"
            f"From: {flight['origin']}\n"
            f"To: {flight['destination']}\n"
            f"Departure: {flight['departure_time']}\n"
            f"Arrival: {flight['arrival_time']}\n"
            f"Price: ${flight['price']}\n"
            f"Aircraft Model: {flight['aircraft_model']}\n"
        )

        messagebox.showinfo("Booking Confirmed", summary)
        self.controller.show_frame("HomePage")

#Starts the application
if __name__ == "__main__":
    app = FlightBookingApp()
    app.selected_flight = None
    app.mainloop()
