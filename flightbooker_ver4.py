import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from PIL import Image, ImageTk

#Constants for file paths
CREDENTIALS_FILE = "app_files/ver4_credentials/credentials.json"
FLIGHTS_FILE = "app_files/flights.json"
LOGO_PATH = "app_files/forfly_logo.png"

#Main application class
class FlightBookingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ForFly") 
        self.geometry("800x600")
        self.center_window()
        
        self.frames = {}
        self.selected_flight = None
        self.load_flights()
        self.create_frames()
        self.show_frame("LoginPage")

    #Centers the window
    def center_window(self):
        window_width = 800
        window_height = 600
        screen_width = self.winfo_screenwidth()  
        screen_height = self.winfo_screenheight()  
        position_top = int(screen_height / 2 - window_height / 2)  
        position_right = int(screen_width / 2 - window_width / 2) 
        self.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')    

    #Loads flight data from JSON file
    def load_flights(self):
        try:
            with open(FLIGHTS_FILE, "r") as f:
                self.flights = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "Flight data file not found.")
            self.flights = []  #Initialize flights as an empty list

    def create_frames(self):
        container = ttk.Frame(self)
        container.pack(expand=True, fill='both')

        #List of page classes to create frames
        for F in (LoginPage, RegisterPage, HomePage, SearchFlightsPage, SelectFlightPage, PassengerInfoPage, ConfirmationPage):
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

        if page_name == "SelectFlightPage":
            frame.update_flight_details()

    #Displays the app logo
    def display_logo(self, parent):
        logo = Image.open(LOGO_PATH)
        logo = logo.resize((250, 70), Image.LANCZOS)
        logo_image = ImageTk.PhotoImage(logo)
        
        logo_label = ttk.Label(parent, image=logo_image)
        logo_label.image = logo_image
        logo_label.pack(pady=10)


#Login page class
class LoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        controller.display_logo(self)

        ttk.Label(self, text="Login", font=("Helvetica", 16)).pack(pady=20)

        self.username = tk.StringVar()
        self.password = tk.StringVar()

        #Username input field
        ttk.Label(self, text="Username:").pack(pady=5)
        ttk.Entry(self, textvariable=self.username).pack(pady=5)

        #Password input field
        ttk.Label(self, text="Password:").pack(pady=5)
        ttk.Entry(self, textvariable=self.password, show="*").pack(pady=5)

        #Login button
        ttk.Button(self, text="Login", command=self.login).pack(pady=10)
        #Button to switch to Register Page
        ttk.Button(self, text="Register", command=lambda: controller.show_frame("RegisterPage")).pack(pady=10)

    def login(self):
        username = self.username.get()
        password = self.password.get()

        try:
            with open(CREDENTIALS_FILE, "r") as f:
                credentials = json.load(f)  #Loads user credentials from file
        except FileNotFoundError:
            messagebox.showerror("Error", "No registered users found.")
            return

        #Checks if the credentials match
        if credentials.get(username) == password:
            self.controller.show_frame("HomePage")
        else:
            messagebox.showerror("Error", "Invalid credentials.")

#Registration page class
class RegisterPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        controller.display_logo(self)

        ttk.Label(self, text="Register", font=("Helvetica", 16)).pack(pady=20)

        self.username = tk.StringVar()
        self.password = tk.StringVar()

        #Username input field
        ttk.Label(self, text="Username:").pack(pady=5)
        ttk.Entry(self, textvariable=self.username).pack(pady=5)

        #Password input field
        ttk.Label(self, text="Password:").pack(pady=5)
        ttk.Entry(self, textvariable=self.password, show="*").pack(pady=5)

        #Register button
        ttk.Button(self, text="Register", command=self.register).pack(pady=10)
        #Back to Login button to switch to login page
        ttk.Button(self, text="Back to Login", command=lambda: controller.show_frame("LoginPage")).pack(pady=10)

    def register(self):
        username = self.username.get()
        password = self.password.get()

        os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)
        
        try:
            with open(CREDENTIALS_FILE, "r") as f:
                credentials = json.load(f)  #Loads existing credentials
        except FileNotFoundError:
            credentials = {}

        #Checks if the username exists
        if username in credentials:
            messagebox.showerror("Error", "Username already exists.")
            return

        #Saves new username and password
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
        controller.display_logo(self)

        #Welcome text
        ttk.Label(self, text="Welcome to the ForFly Flight Booking App!", font=("Helvetica", 16)).pack(pady=20)

        # Button to switch to search flights page
        ttk.Button(self, text="Search Flights", command=lambda: controller.show_frame("SearchFlightsPage")).pack(pady=10)

#Search flights page class
class SearchFlightsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        controller.display_logo(self)

        ttk.Label(self, text="Search Flights", font=("Helvetica", 16)).pack(pady=20)

        self.origins = sorted(set(flight['origin'] for flight in controller.flights))
        self.destinations = sorted(set(flight['destination'] for flight in controller.flights))

        self.origin = tk.StringVar()
        self.destination = tk.StringVar()

        #Label and combobox for selecting origin
        ttk.Label(self, text="Origin:").pack(pady=5)
        self.origin_combobox = ttk.Combobox(self, textvariable=self.origin, values=self.origins, width=40)
        self.origin_combobox.pack(pady=5)
        #Update destination options based on selected origin
        self.origin_combobox.bind("<<ComboboxSelected>>", self.update_destinations)

        #Label and combobox for selecting destination
        ttk.Label(self, text="Destination:").pack(pady=5)
        self.destination_combobox = ttk.Combobox(self, textvariable=self.destination, width=40)
        self.destination_combobox.pack(pady=5)
        #Check if valid destination is selected
        self.destination_combobox.bind("<<ComboboxSelected>>", self.check_destination)

        ttk.Button(self, text="Search", command=self.search_flights).pack(pady=10)

        self.results_frame = ttk.Frame(self)
        self.results_frame.pack(pady=10)

        self.update_destinations()

    def update_destinations(self, event=None):
        #Updates destinations based on the selected origin
        selected_origin = self.origin.get()
        if selected_origin:
            #Gets destinations valid from the selected origin
            destinations = sorted(set(flight['destination'] for flight in self.controller.flights if flight['origin'] == selected_origin))
            if destinations:
                self.destination_combobox.config(values=destinations)
                self.destination_combobox.set('')
            else:
                self.destination_combobox.config(values=["No destinations available"])
                self.destination_combobox.set('No destinations available')
        else:
            self.destination_combobox.config(values=["Please choose an origin first."])
            self.destination_combobox.set('Please choose an origin first.')

    def check_destination(self, event):
        #Check if a destination is selected after an origin
        selected_destination = self.destination.get()
        if selected_destination == "Please choose an origin first.":
            messagebox.showwarning("Warning", "Please choose an origin first.")
            self.destination_combobox.set('')

    def search_flights(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        origin = self.origin.get()
        destination = self.destination.get()

        #Checks if both origin and destination are selected
        if origin == "" or destination == "" or destination == "Please choose an origin first.":
            messagebox.showwarning("Warning", "Please select both origin and destination.")
            return

        #Searches for flights matching the origin and destination
        results = [flight for flight in self.controller.flights if flight["origin"] == origin and flight["destination"] == destination]

        if not results:
            ttk.Label(self.results_frame, text="No flights found.").pack()
        else:
            for flight in results:
                flight_frame = ttk.Frame(self.results_frame)
                flight_frame.pack(pady=5)

                #Display the airline logo
                logo_path = flight["logo"]
                if os.path.isfile(logo_path):
                    logo_image = Image.open(logo_path)
                    logo_image = logo_image.resize((50, 50), Image.LANCZOS)
                    logo_photo = ImageTk.PhotoImage(logo_image)
                    logo_label = ttk.Label(flight_frame, image=logo_photo)
                    logo_label.image = logo_photo
                    logo_label.pack(side=tk.LEFT, padx=10)

                #Button to select the flight
                select_button = ttk.Button(flight_frame, text=f"Flight {flight['flight_number']} - from ${flight['price']:.2f}",
                                           command=lambda f=flight: self.select_flight(f))
                select_button.pack(side=tk.LEFT, padx=10)

                #Displays flight details
                details_label = ttk.Label(flight_frame, text=f"Departure: {flight['departure_time']} | "
                                                             f"Arrival: {flight['arrival_time']} | "
                                                             f"Aircraft: {flight['aircraft_model']}")
                details_label.pack(side=tk.LEFT, padx=10)

    def select_flight(self, flight):
        self.controller.selected_flight = flight
        self.controller.show_frame("SelectFlightPage")

#Select flight page class
class SelectFlightPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        controller.display_logo(self)

        ttk.Label(self, text="Confirm Flight Details and Select Seat Class", font=("Helvetica", 16)).pack(pady=20)

        #Variable to hold flight details
        self.flight_details = tk.StringVar()
        ttk.Label(self, textvariable=self.flight_details).pack(pady=10)

        #Variables to hold selected class and ticket type
        self.class_selection = tk.StringVar()
        self.ticket_type_selection = tk.StringVar()

        #Flight class options and price multipliers
        self.class_options = ["First Class", "Business Class", "Premium Economy", "Economy"]
        self.price_multipliers = {"First Class": 3.5, "Business Class": 2.5, "Premium Economy": 1.75, "Economy": 1.0}

        #Ticket type options and multipliers
        self.ticket_types = ["Child (under 13)", "Adult (13+)"]
        self.ticket_type_multipliers = {"Child (under 13)": 0.5, "Adult (13+)": 1.0}

        self.class_frame = ttk.Frame(self)
        self.class_frame.pack(pady=5)
        
        self.ticket_type_frame = ttk.Frame(self)
        self.ticket_type_frame.pack(pady=5)

        #Labels for flight class and ticket type selection
        ttk.Label(self.class_frame, text="Select Flight Class", font=("Helvetica", 16)).pack(pady=20)
        ttk.Label(self.ticket_type_frame, text="Select Ticket Type", font=("Helvetica", 16)).pack(pady=20)

        ttk.Button(self, text="Next", command=self.select_class).pack(pady=20)

    def update_flight_details(self):
        #Updates displayed flight details based on the selected flight
        flight = self.controller.selected_flight
        if flight is not None:
            self.flight_details.set(f"Flight Number: {flight['flight_number']}\n"
                                    f"Origin: {flight['origin']}\n"
                                    f"Destination: {flight['destination']}\n"
                                    f"Departure Time: {flight['departure_time']}\n"
                                    f"Arrival Time: {flight['arrival_time']}")

            for widget in self.class_frame.winfo_children():
                if not isinstance(widget, ttk.Label): 
                    widget.destroy()

            for widget in self.ticket_type_frame.winfo_children():
                if not isinstance(widget, ttk.Label):
                    widget.destroy()

            #Creates radio buttons for class options with new calculated prices
            for class_option in self.class_options:
                multiplier = self.price_multipliers[class_option]
                ticket_multiplier = self.ticket_type_multipliers[self.ticket_type_selection.get() or "Adult (13+)"]
                price = flight["price"] * multiplier * ticket_multiplier
                ttk.Radiobutton(self.class_frame, text=f"{class_option} - ${price:.2f}",
                                variable=self.class_selection, value=class_option).pack(side=tk.LEFT, padx=5)

            #Create radio buttons for ticket type options
            for ticket_type in self.ticket_types:
                ttk.Radiobutton(self.ticket_type_frame, text=ticket_type,
                                variable=self.ticket_type_selection, value=ticket_type,
                                command=self.update_flight_details).pack(side=tk.LEFT, padx=5)
        else:
            self.flight_details.set("No flight selected")

    def select_class(self):
        #Checks both class and ticket type are selected
        if not self.class_selection.get() or not self.ticket_type_selection.get():
            messagebox.showwarning("Warning", "Please select both a flight class and a ticket type.")
            return

        #Calculate final price based on selections
        flight_class = self.class_selection.get()
        ticket_type = self.ticket_type_selection.get()
        base_price = self.controller.selected_flight["price"] * self.price_multipliers[flight_class]
        final_price = base_price * self.ticket_type_multipliers[ticket_type]

        self.controller.selected_flight["class"] = flight_class
        self.controller.selected_flight["ticket_type"] = ticket_type
        self.controller.selected_flight["final_price"] = final_price

        self.controller.show_frame("PassengerInfoPage")

#Passenger info page class
class PassengerInfoPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        controller.display_logo(self)

        ttk.Label(self, text="Passenger Information", font=("Helvetica", 16)).pack(pady=20)

        self.name = tk.StringVar()
        self.age = tk.StringVar()

        #Entry for passenger name
        ttk.Label(self, text="Name:").pack(pady=5)
        self.name_entry = ttk.Entry(self, textvariable=self.name)
        self.name_entry.pack(pady=5)

        #Entry for passenger age
        ttk.Label(self, text="Age:").pack(pady=5)
        self.age_entry = ttk.Entry(self, textvariable=self.age)
        self.age_entry.pack(pady=5)

        ttk.Button(self, text="Next", command=self.validate_and_proceed).pack(pady=10)
        ttk.Button(self, text="Back", command=lambda: controller.show_frame("SelectFlightPage")).pack(pady=10)

    def validate_and_proceed(self):
        age = self.age.get()
        #Checks if the age is a digit
        if not age.isdigit():
            messagebox.showwarning("Warning", "Please enter a valid age.")
            return

        #Convert age to an integer
        age = int(age)
        ticket_type = self.controller.selected_flight["ticket_type"]
        #Validate age against the selected ticket type
        if (ticket_type == "Child (under 13)" and age >= 13) or (ticket_type == "Adult (13+)" and age < 13):
            messagebox.showwarning("Warning", f"Age does not match the selected ticket type: {ticket_type}.")
            return

        #Capitalize the passenger name
        self.capitalize_and_set_passenger_name()
        self.controller.show_frame("ConfirmationPage")

    def capitalize_and_set_passenger_name(self):
        #Capitalize the passenger name
        capitalized_name = self.name.get().title()
        self.name.set(capitalized_name)

#Confirmation page class
class ConfirmationPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        controller.display_logo(self)

        ttk.Label(self, text="Confirmation", font=("Helvetica", 16)).pack(pady=20)

        self.confirmation_details = tk.StringVar()
        ttk.Label(self, textvariable=self.confirmation_details).pack(pady=10)

        #Button to confirm the booking
        ttk.Button(self, text="Confirm Booking", command=self.finish).pack(pady=20)

    def update_confirmation_details(self):
        #Updates the confirmation details with flight and passenger information
        flight = self.controller.selected_flight
        if flight is not None:
            passenger_name = self.controller.frames["PassengerInfoPage"].name.get()
            passenger_age = self.controller.frames["PassengerInfoPage"].age.get()

            #Confirmation details displayed
            self.confirmation_details.set(f"Flight Number: {flight['flight_number']}\n"
                                          f"Origin: {flight['origin']}\n"
                                          f"Destination: {flight['destination']}\n"
                                          f"Departure Time: {flight['departure_time']}\n"
                                          f"Arrival Time: {flight['arrival_time']}\n"
                                          f"Class: {flight['class']}\n"
                                          f"Ticket Type: {flight['ticket_type']}\n"
                                          f"Price: ${flight['final_price']:.2f}\n\n"
                                          f"Passenger Name: {passenger_name}\n"
                                          f"Passenger Age: {passenger_age}")
        else:
            self.confirmation_details.set("No flight selected")

    def finish(self):
        messagebox.showinfo("Success", "Booking confirmed!")
        self.controller.show_frame("HomePage")

#Starts the application
if __name__ == "__main__":
    app = FlightBookingApp()
    app.mainloop()
