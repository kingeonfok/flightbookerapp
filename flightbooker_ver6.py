import tkinter as tk
import json
import os
import re
import datetime
import ssl
import smtplib
import base64
import threading
import qrcode
from tkinter import ttk, messagebox
from tkinter import font
from datetime import date
from email.message import EmailMessage
from PIL import Image, ImageTk
from tkcalendar import DateEntry
from hashlib import sha256

#Constants for file paths
CREDENTIALS_FILE = "app_files/ver6_credentials/credentials.json"
FLIGHTS_FILE = "app_files/flights.json"
BOOKINGS_FILE = "app_files/bookings.json"
LOGO_PATH = "app_files/forfly_logo.png"

large_font = ("Helvetica", 13)

class FlightBookingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()
        self.title("ForFly")
        self.geometry("800x850")
        self.center_window()
        
        self.frames = {}
        self.selected_flight = None
        self.load_flights()
        self.username = None
        self.current_username = None
        self.bookings = {}
        self.create_frames()
        self.show_frame("LoginPage")
        

    def center_window(self):
        window_width = 800
        window_height = 850
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')    

    def load_flights(self):
        #Load flight data from the JSON file
        try:
            with open(FLIGHTS_FILE, "r") as f:
                self.flights = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "Flight data file not found.")
            self.flights = []

    def load_bookings(self, username):
        #Load user bookings from JSON file
        try:
            with open(BOOKINGS_FILE, "r") as f:
                self.bookings = json.load(f)
                if not isinstance(self.bookings, dict):
                    self.bookings = {}
                if username in self.bookings:
                    user_bookings = self.bookings[username]
                    for booking in user_bookings:
                        if 'flight_date' in booking and isinstance(booking['flight_date'], str):
                            booking['flight_date'] = date.fromisoformat(booking['flight_date'])
                else:
                    self.bookings[username] = []
        except FileNotFoundError:
            self.bookings = {username: []}
        except json.JSONDecodeError:
            self.bookings = {username: []}

    #Saves user's booking to the JSON file
    def save_booking(self, username, booking_info):
        with self.lock:
            try:
                if 'flight_date' in booking_info and isinstance(booking_info['flight_date'], date):
                    booking_info['flight_date'] = booking_info['flight_date'].isoformat() # Convert date to ISO format

                if username not in self.bookings:
                    self.bookings[username] = []

                for old_booking in self.bookings[username]:
                    if 'flight_date' in old_booking and isinstance(old_booking['flight_date'], date):
                        old_booking['flight_date'] = old_booking['flight_date'].isoformat()

                #Appends booking info to the user's bookings
                self.bookings[username].append(booking_info)

                #Saves bookings to JSON file
                with open(BOOKINGS_FILE, "w") as f:
                    json.dump(self.bookings, f, indent=4)

            except Exception as e:
                print(f"Error saving booking: {e}")



    def login(self, username):
        self.current_username = username #Stores the logged-in username
        self.load_bookings(username) #Load the user's bookings
        self.show_frame("HomePage")

    def create_frames(self):
        container = ttk.Frame(self)
        container.pack(expand=True, fill='both')

        #List of frame classes
        for F in (LoginPage, RegisterPage, HomePage, SearchFlightsPage, SelectFlightPage, PassengerInfoPage, ConfirmationPage, CreditCardPage, OtherDetailsPage, BookingsPage):
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

        #Update details if frames is shown
        if page_name == "SelectFlightPage":
            frame.update_flight_details()

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

        ttk.Label(self, text="Welcome to ForFly, Please login.", font=("Helvetica", 18)).pack(pady=20)

        self.username = tk.StringVar()
        self.password = tk.StringVar()

        #Username input
        ttk.Label(self, text="Username:", font=large_font).pack(pady=5)
        ttk.Entry(self, textvariable=self.username).pack(pady=5)

        #Password input
        ttk.Label(self, text="Password:", font=large_font).pack(pady=5)
        ttk.Entry(self, textvariable=self.password, show="*").pack(pady=5)

        #Buttons for login and registration
        ttk.Button(self, text="Login", command=self.login).pack(pady=10)
        ttk.Button(self, text="No account yet? Register here!", command=lambda: controller.show_frame("RegisterPage")).pack(pady=10)

    def login(self):
        username = self.username.get()
        password = self.password.get()
        hashed_password = sha256(password.encode()).hexdigest() #Encrypt the password

        #Load credentials from file
        try:
            with open(CREDENTIALS_FILE, "r") as f:
                credentials = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "No registered users found.")
            return

        #Check if the credentials match
        if credentials.get(username) == hashed_password:
            self.controller.current_username = username
            self.controller.load_bookings(username)  #Load the user's bookings
            self.controller.frames["BookingsPage"].display_bookings()
            self.controller.show_frame("HomePage")

        else:
            messagebox.showerror("Error", "Invalid credentials.")


#Register page class
class RegisterPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        controller.display_logo(self)

        ttk.Label(self, text="New to ForFly? Register here!", font=("Helvetica", 18)).pack(pady=20)

        self.username = tk.StringVar()
        self.password = tk.StringVar()

        #Username input
        ttk.Label(self, text="Username:", font=large_font).pack(pady=5)
        ttk.Entry(self, textvariable=self.username).pack(pady=5)

        #Password input
        ttk.Label(self, text="Password:", font=large_font).pack(pady=5)
        ttk.Entry(self, textvariable=self.password, show="*").pack(pady=5)

        ttk.Button(self, text="Register", command=self.register).pack(pady=10)
        ttk.Button(self, text="Already have a login? Go back to Login here.", command=lambda: controller.show_frame("LoginPage")).pack(pady=10)

    def register(self):
        username = self.username.get()
        password = self.password.get()
        hashed_password = sha256(password.encode()).hexdigest() #Encrypt the password

        os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)
        
        try:
            with open(CREDENTIALS_FILE, "r") as f:
                credentials = json.load(f)
        except FileNotFoundError:
            credentials = {}

        #Check if the username already exist
        if username in credentials:
            #Show error message if the username is taken
            messagebox.showerror("Error", "Username already exists.")
            return

        #Store the new username and password in the dictionary
        credentials[username] = hashed_password
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

        #Welcome message
        ttk.Label(self, text="Welcome to the ForFly Flight Booking App!", font=("Helvetica", 18)).pack(pady=20)
        ttk.Label(self, text="What would you like to do today?", font=("Helvetica", 16)).pack(pady=0)

        ttk.Button(self, text="Search and Book Flights", command=lambda: controller.show_frame("SearchFlightsPage")).pack(pady=20)
        ttk.Button(self, text="Show All Bookings", command=lambda: controller.show_frame("BookingsPage")).pack(pady=20)

#Bookings page class
class BookingsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        controller.display_logo(self)
        
        ttk.Label(self, text="Your Bookings", font=("Helvetica", 18)).pack(pady=20)

        self.bookings_frame = ttk.Frame(self)
        self.bookings_frame.pack(pady=10)

        #Dictionary to track the state of toggle for flight details
        self.toggle_states = {}

        ttk.Button(self, text="Back to Home", command=lambda: controller.show_frame("HomePage")).pack(pady=20)

    def display_bookings(self):
        self.toggle_states = {}
        for widget in self.bookings_frame.winfo_children():
            widget.destroy()

        #Get the current user's bookings from the controller
        username = self.controller.current_username
        user_bookings = self.controller.bookings.get(username, [])

        #Display a message if there are no bookings for the user
        if not user_bookings:
            ttk.Label(self.bookings_frame, text="No bookings found.", font=("Helvetica", 14)).pack()
            return

        #Sort the bookings by flight date
        sorted_bookings = sorted(user_bookings, key=lambda b: b.get("flight_date", ""))

        last_date = None 

        for booking in sorted_bookings:
            flight_number = booking.get("flight_number", "N/A")
            flight_date = booking.get("flight_date", "N/A")
            passenger_name = booking.get("passenger_name", "N/A")
            departure_time = booking.get("departure_time", "N/A")

            if isinstance(flight_date, str):
                try:
                    date_obj = datetime.datetime.strptime(flight_date, "%Y-%m-%d").date()
                except ValueError:
                    formatted_date = flight_date 
            else:
                date_obj = flight_date 

            #Format the date
            formatted_date = date_obj.strftime("%B {day}, %Y").replace("{day}", str(date_obj.day) + self.get_day_suffix(date_obj.day))

            #Add a new date header
            if flight_date != last_date:
                ttk.Label(self.bookings_frame, text=f"Flights for {formatted_date}", font=("Helvetica", 14, "bold")).pack(pady=10)
                last_date = flight_date

            flight_data = next((flight for flight in self.controller.flights if flight["flight_number"] == flight_number), None)
            logo_path = flight_data["logo"] if flight_data else None

            booking_frame = ttk.Frame(self.bookings_frame)
            booking_frame.pack(pady=5)

            #Display the airline logo
            if logo_path and os.path.isfile(logo_path):
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((50, 50), Image.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_image)
                logo_label = ttk.Label(booking_frame, image=logo_photo)
                logo_label.image = logo_photo
                logo_label.pack(side=tk.LEFT, padx=5)

            #Display basic flight information
            booking_label = ttk.Label(
                booking_frame,
                text=f"Flight {flight_number} booked for {passenger_name}",
                font=("Helvetica", 12)
            )
            booking_label.pack(side=tk.LEFT, padx=5)

            #Create frame for additional flight details
            details_frame = ttk.Frame(booking_frame)
            details_frame.pack(fill="x", pady=5)

            details_inner_frame = ttk.Frame(details_frame)
            details_inner_frame.pack(fill="x", pady=5, padx=10)
            details_inner_frame.pack_forget()

            #Button to toggle the visibility of additional flight details
            toggle_button = ttk.Button(
                details_frame,
                text="Expand",
                command=lambda f=flight_number: self.toggle_details(f)
            )
            toggle_button.pack(pady=5)

            self.toggle_states[flight_number] = {
                'button': toggle_button,
                'frame': details_inner_frame,
                'expanded': False
            }

    def get_day_suffix(self, day):
        """Helper method to return the ordinal suffix for a day."""
        if 4 <= day <= 20 or 24 <= day <= 30:
            return "th"
        else:
            return {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

    def toggle_details(self, flight_number):
        toggle_info = self.toggle_states[flight_number]
        details_frame = toggle_info['frame']
        
        if toggle_info['expanded']:
            details_frame.pack_forget()
            toggle_info['button'].config(text="Expand") #Change the button text to expand
            
            #Clear existing labels
            for widget in details_frame.winfo_children():
                widget.destroy()
        else:
            #Show the additional flight details
            details_frame.pack(fill="x", pady=5)
            toggle_info['button'].config(text="Collapse")  #Change the button text to collaspe

            #Retrieve the passenger details for the selected flight
            passenger_details = self.controller.bookings[self.controller.current_username]

            #Find the correct booking
            booking_info = next((booking for booking in passenger_details if booking['flight_number'] == flight_number), None)

            if booking_info:
                #Generate a QR code
                qr_info = f"Flight Number: {booking_info['flight_number']}\nPassenger: {booking_info['passenger_name']}"
                qr = qrcode.make(qr_info)
                qr_path = "app_files/temp_qr.png"  #Temporary file for storing the QR code
                qr.save(qr_path)
                
                #Load the QR code image
                qr_image = Image.open(qr_path)
                qr_image = qr_image.resize((100, 100), Image.LANCZOS)
                qr_photo = ImageTk.PhotoImage(qr_image)

                if not any(isinstance(widget, tk.Label) and widget.cget("text") == "Your Boarding Pass" for widget in details_frame.winfo_children()):
                    title_label = tk.Label(details_frame, text="Your Boarding Pass", font=("Helvetica", 14, "bold"))
                    title_label.pack(pady=5)

                #Display the QR code image
                if not any(isinstance(widget, tk.Label) and widget.cget("text") == qr_info for widget in details_frame.winfo_children()):
                    qr_label = tk.Label(details_frame, image=qr_photo)
                    qr_label.image = qr_photo
                    qr_label.pack(pady=5)

                #Add flight details below the QR code
                details = (
                    f"Passenger Name: {booking_info['passenger_name']}\n"
                    f"Flight Number: {booking_info['flight_number']}\n"
                    f"Origin: {booking_info['origin']}\n"
                    f"Destination: {booking_info['destination']}\n"
                    f"Departure: {booking_info['departure_time']}\n"
                    f"Class: {booking_info['class']}\n"
                    f"Ticket Type: {booking_info['ticket_type']}\n"
                    f"Phone Number: {booking_info['phone_number']}"
                )
                
                #Display flight details below the QR code
                details_label = tk.Label(details_frame, text=details, font=("Helvetica", 12))
                details_label.pack(fill="x", padx=10, pady=5)

        toggle_info['expanded'] = not toggle_info['expanded']

#Search flights page class
class SearchFlightsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        controller.display_logo(self)

        ttk.Label(self, text="Search Flights", font=("Helvetica", 18)).pack(pady=20)
    
        #Origins and destinations from available flights
        self.origins = sorted(set(flight['origin'] for flight in controller.flights))
        self.destinations = sorted(set(flight['destination'] for flight in controller.flights))

        self.origin = tk.StringVar()
        self.destination = tk.StringVar()

        #Origin selection combobox
        ttk.Label(self, text="Origin:", font=large_font).pack(pady=5)
        self.origin_combobox = ttk.Combobox(self, textvariable=self.origin, values=self.origins, width=40)
        self.origin_combobox.pack(pady=5)
        self.origin_combobox.bind("<<ComboboxSelected>>", self.update_destinations)

        #Destination selection combobox
        ttk.Label(self, text="Destination:", font=large_font).pack(pady=5)
        self.destination_combobox = ttk.Combobox(self, textvariable=self.destination, width=40)
        self.destination_combobox.pack(pady=5)
        self.destination_combobox.bind("<<ComboboxSelected>>", self.check_destination)

        #Departure date entry
        ttk.Label(self, text="Departure Date:", font=large_font).pack(pady=5)
        self.depart_date_entry = DateEntry(self, width=40, background='royalblue', foreground='white', borderwidth=2)
        self.depart_date_entry.pack(pady=5)

        self.controller.depart_date = self.depart_date_entry

        ttk.Button(self, text="Search", command=self.search_flights).pack(pady=10)
        ttk.Button(self, text="Back to Home", command=lambda: controller.show_frame("HomePage")).pack(pady=(10, 20))

        self.results_frame = ttk.Frame(self)
        self.results_frame.pack(pady=10)

        #Updates destination options based on origin
        self.update_destinations()

    def update_destinations(self, event=None):
        selected_origin = self.origin.get()
        if selected_origin:
            #Filter available destinations based on the origin
            destinations = sorted(set(flight['destination'] for flight in self.controller.flights if flight['origin'] == selected_origin))
            if destinations:
                #Update the destination combobox with the filtered values
                self.destination_combobox.config(values=destinations)
                self.destination_combobox.set('')
            else:
                self.destination_combobox.config(values=["No destinations available"])
                self.destination_combobox.set('No destinations available')
        else:
            #Prompt the user to select an origin first if none is selected
            self.destination_combobox.config(values=["Please choose an origin first."])
            self.destination_combobox.set('Please choose an origin first.')

    def check_destination(self, event):
        selected_destination = self.destination.get()
        #Warn user if they try to select a destination without selecting an origin
        if selected_destination == "Please choose an origin first.":
            messagebox.showwarning("Warning", "Please choose an origin first.")
            self.destination_combobox.set('')

    def search_flights(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        origin = self.origin.get()
        destination = self.destination.get()
        depart_date = self.depart_date_entry.get_date() if self.depart_date_entry.get_date() else ""

        #Check if both origin and destination are selected
        if origin == "" or destination == "" or destination == "Please choose an origin first.":
            messagebox.showwarning("Warning", "Please select both origin and destination.")
            return

        #Filter flights based on selected origin and destination
        results = [flight for flight in self.controller.flights if flight["origin"] == origin and flight["destination"] == destination]

        if not results:
            #Show message if no flights found
            ttk.Label(self.results_frame, text="No flights found.", font=large_font).pack()
        else:
            #Display flights found in the search results
            for flight in results:
                flight_frame = ttk.Frame(self.results_frame)
                flight_frame.pack(pady=5)

                #Load and display the airline logo
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

                #Display flight details
                details_label = ttk.Label(flight_frame, text=f"Departure: {flight['departure_time']} | "
                                                            f"Arrival: {flight['arrival_time']} | "
                                                            f"Aircraft: {flight['aircraft_model']}", font=large_font)
                details_label.pack(side=tk.LEFT, padx=10)

    def select_flight(self, flight):
        #Stores the selected flight and its date
        selected_date = self.depart_date_entry.get_date()
        self.controller.selected_flight = flight
        self.controller.selected_flight["flight_date"] = selected_date.strftime("%Y-%m-%d")
        self.controller.selected_flight["fare"] = flight["price"]  # Store the fare
        self.controller.show_frame("SelectFlightPage")
    

#Select flight page class
class SelectFlightPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        controller.display_logo(self)

        ttk.Label(self, text="Confirm Flight Details and Select Seat Class", font=("Helvetica", 18)).pack(pady=20)

        #Variable to hold flight details for display
        self.flight_details = tk.StringVar()
        ttk.Label(self, textvariable=self.flight_details, font=large_font).pack(pady=10)

        #Variables to hold selected class and ticket type
        self.class_selection = tk.StringVar()
        self.ticket_type_selection = tk.StringVar()

        #Flight class options and their price multipliers
        self.class_options = ["First Class", "Business Class", "Premium Economy", "Economy"]
        self.price_multipliers = {"First Class": 3.5, "Business Class": 2.5, "Premium Economy": 1.75, "Economy": 1.0}

        self.ticket_types = ["Child (under 13)", "Adult (13+)"]
        self.ticket_type_multipliers = {"Child (under 13)": 0.5, "Adult (13+)": 1.0}

        self.class_frame = ttk.Frame(self)
        self.class_frame.pack(pady=5)
        
        self.ticket_type_frame = ttk.Frame(self)
        self.ticket_type_frame.pack(pady=5)

        ttk.Label(self.class_frame, text="Select Flight Class", font=("Helvetica", 18)).pack(pady=20)
        ttk.Label(self.ticket_type_frame, text="Select Ticket Type", font=("Helvetica", 18)).pack(pady=20)

        ttk.Button(self, text="Continue Booking", command=self.select_class).pack(pady=20)
        
        ttk.Button(self, text="Back to see other flights", command=self.go_back).pack(pady=10)

    def update_flight_details(self):
        flight = self.controller.selected_flight
        if flight is not None:
            self.flight_details.set(f"Flight Number: {flight['flight_number']}\n"
                                    f"Origin: {flight['origin']}\n"
                                    f"Destination: {flight['destination']}\n"
                                    f"Flight Date: {flight['flight_date']}\n"
                                    f"Departure Time: {flight['departure_time']}\n"
                                    f"Arrival Time: {flight['arrival_time']}")

            #Clear the previous class and ticket type options
            for widget in self.class_frame.winfo_children():
                if not isinstance(widget, ttk.Label):
                    widget.destroy()

            for widget in self.ticket_type_frame.winfo_children():
                if not isinstance(widget, ttk.Label):
                    widget.destroy()

            # =Display flight class options with prices
            base_price = flight["fare"]
            ticket_type_multiplier = self.ticket_type_multipliers[self.ticket_type_selection.get() or "Adult (13+)"]

            for class_option in self.class_options:
                class_multiplier = self.price_multipliers[class_option]
                price = base_price * class_multiplier * ticket_type_multiplier
                ttk.Radiobutton(self.class_frame, text=f"{class_option} - ${price:.2f}",
                                variable=self.class_selection, value=class_option).pack(side=tk.LEFT, padx=5)

            #Displays ticket type options
            for ticket_type in self.ticket_types:
                ttk.Radiobutton(self.ticket_type_frame, text=ticket_type,
                                variable=self.ticket_type_selection, value=ticket_type,
                                command=self.update_flight_details).pack(side=tk.LEFT, padx=5)
        else:
            self.flight_details.set("No flight selected")


    def go_back(self):
        self.controller.show_frame("SearchFlightsPage")

    def select_class(self):
        #Check that both class and ticket type are selected
        if not self.class_selection.get() or not self.ticket_type_selection.get():
            messagebox.showwarning("Warning", "Please select both a flight class and a ticket type.")
            return

        flight_class = self.class_selection.get()
        ticket_type = self.ticket_type_selection.get()

        #Calculates the final price based on the selected flight class and ticket type
        base_price = self.controller.selected_flight["fare"]
        class_multiplier = self.price_multipliers[flight_class]
        ticket_type_multiplier = self.ticket_type_multipliers[ticket_type]
        
        final_price = base_price * class_multiplier * ticket_type_multiplier

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

        ttk.Label(self, text="Passenger Information", font=("Helvetica", 18)).pack(pady=20)

        self.name = tk.StringVar()
        self.age = tk.StringVar()

        #Entry for passenger name
        ttk.Label(self, text="Name:", font=large_font).pack(pady=5)
        self.name_entry = ttk.Entry(self, textvariable=self.name)
        self.name_entry.pack(pady=5)

        #Entry for passenger age
        ttk.Label(self, text="Age:", font=large_font).pack(pady=5)
        self.age_entry = ttk.Entry(self, textvariable=self.age)
        self.age_entry.pack(pady=5)

        ttk.Button(self, text="Continue Booking", command=self.validate_and_proceed).pack(pady=10)
        ttk.Button(self, text="Back to Flight Class selection", command=lambda: controller.show_frame("SelectFlightPage")).pack(pady=10)

    def validate_and_proceed(self):
        age = self.age.get()

        #Check if the name is provided
        if not self.name.get():
            messagebox.showwarning("Warning", "Please enter a name.")
            return

        #Check if the age is a digit and is valid
        if not age.isdigit():
            messagebox.showwarning("Warning", "Please enter a valid age.")
            return

        age = int(age) #Convert age to integer
        ticket_type = self.controller.selected_flight["ticket_type"]

        if (ticket_type == "Child (under 13)" and age >= 13) or (ticket_type == "Adult (13+)" and age < 13):
            messagebox.showwarning("Warning", f"Age does not match the selected ticket type: {ticket_type}.")
            return

        self.capitalize_and_set_passenger_name() #Capitalize and set the passenger name

        #Saves the selected flight date
        flight_date = self.controller.depart_date.get_date() if self.controller.depart_date.get_date() else ""
        self.controller.selected_flight["flight_date"] = flight_date

        #Saves passenger name and age
        self.controller.selected_flight["passenger_name"] = self.name.get()
        self.controller.selected_flight["passenger_age"] = age

        #Update confirmation page with flight date and details
        self.controller.frames["ConfirmationPage"].update_confirmation_details()

        self.controller.show_frame("CreditCardPage")

    def capitalize_and_set_passenger_name(self):
        capitalized_name = self.name.get().title()
        self.name.set(capitalized_name)

#Credit card entering page class
class CreditCardPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        controller.display_logo(self)

        ttk.Label(self, text="Credit Card Details", font=("Helvetica", 18)).pack(pady=(10, 20))

        self.card_number = tk.StringVar()
        self.expiry_month = tk.StringVar()
        self.expiry_year = tk.StringVar()
        self.cvc = tk.StringVar()

        #Variables for credit card input fields
        ttk.Label(self, text="Card Number:", font=large_font).pack(pady=(10, 5))
        self.card_entry = ttk.Entry(self, textvariable=self.card_number)
        self.card_entry.pack(pady=(0, 15))
        self.card_entry.bind("<KeyRelease>", self.format_card_number)

        #Expiry date section
        ttk.Label(self, text="Expiry Date:", font=large_font).pack(pady=(0, 5))

        expiry_frame = ttk.Frame(self)
        expiry_frame.pack(pady=(0, 15))

        #Expiry month dropdown
        ttk.Label(expiry_frame, text="Month:", font=large_font).pack(side=tk.LEFT, padx=(0, 5))
        self.expiry_month_menu = ttk.Combobox(expiry_frame, textvariable=self.expiry_month, values=[f"{i:02d}" for i in range(1, 13)], width=5)
        self.expiry_month_menu.pack(side=tk.LEFT, padx=(0, 15))

        #Expiry year dropdown
        ttk.Label(expiry_frame, text="Year:", font=large_font).pack(side=tk.LEFT, padx=(0, 5))
        self.expiry_year_menu = ttk.Combobox(expiry_frame, textvariable=self.expiry_year, values=[str(year) for year in range(2024, 2034)], width=8)
        self.expiry_year_menu.pack(side=tk.LEFT)

        #CVC input field
        ttk.Label(self, text="CVC:", font=large_font).pack(pady=(0, 5))
        self.cvc_entry = ttk.Entry(self, textvariable=self.cvc, show='*') #Hide CVC input
        self.cvc_entry.pack(pady=(0, 15))
        self.cvc_entry.bind("<KeyRelease>", self.limit_cvc_input) #Limit CVC input length

        ttk.Button(self, text="Continue Booking", command=self.validate_and_proceed).pack(pady=(10, 5))
        ttk.Button(self, text="Back to Passenger Information", command=lambda: controller.show_frame("PassengerInfoPage")).pack(pady=(15, 20))

    def format_card_number(self, event):
        #Format card number as the user types
        card_number = self.card_number.get().replace(" ", "")
        if len(card_number) > 16:  #Limits to 16 digits
            card_number = card_number[:16]
        formatted_number = " ".join(card_number[i:i+4] for i in range(0, len(card_number), 4)) #Adds spaces
        self.card_number.set(formatted_number)
        self.card_entry.icursor(len(formatted_number))

    def limit_cvc_input(self, event):
        #Limit CVC input to a maximum of 4 digits
        cvc = self.cvc.get()
        if len(cvc) > 4:
            self.cvc.set(cvc[:4])

    def validate_and_proceed(self):
        #Validate credit card details
        card_number = self.card_number.get()
        expiry_month = self.expiry_month.get()
        expiry_year = self.expiry_year.get()
        cvc = self.cvc.get()

        if not (card_number and expiry_month and expiry_year and cvc):
            messagebox.showwarning("Warning", "Please enter all credit card details.")  #Warn if fields are empty
            return

        if not self.validate_card_number(card_number):
            messagebox.showwarning("Warning", "Invalid card number.")  #Warn if card number is invalid
            return

        if not self.validate_expiry_date(expiry_month, expiry_year):
            messagebox.showwarning("Warning", "Invalid expiry date.")  #Warn if expiry date is invalid
            return

        if not self.validate_cvc(cvc):
            messagebox.showwarning("Warning", "Invalid CVC.")  #Warn if CVC is invalid
            return

        self.controller.show_frame("OtherDetailsPage")

    def validate_card_number(self, card_number):
        #Validate the card number format and check validity using Luhn's algorithm
        card_number = card_number.replace(" ", "")
        if not re.match(r"^\d{13,19}$", card_number):
            return False
        return self.luhn_algorithm(card_number)  #Validate with Luhn's algorithm

    def validate_expiry_date(self, month, year):
        #Validate the expiry date of the card
        if not (re.match(r"^\d{2}$", month) and re.match(r"^\d{4}$", year)):
            return False
        current_date = datetime.datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        expiry_year = int(year)
        expiry_month = int(month)
        #Check if the expiry date is in the future
        if expiry_year < current_year or (expiry_year == current_year and expiry_month < current_month):
            return False
        return True

    def validate_cvc(self, cvc):
        #Validate CVC input format
        return re.match(r"^\d{3,4}$", cvc) is not None  #Must be 3 or 4 digits

    def luhn_algorithm(self, card_number):
        #Use the Luhn algorithm to check card validity
        total = 0
        reverse_digits = card_number[::-1]
        for i, digit in enumerate(reverse_digits):
            n = int(digit)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            total += n
        return total % 10 == 0
        self.controller.show_frame("OtherDetailsPage")

#Other details page class
class OtherDetailsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        controller.display_logo(self)

        ttk.Label(self, text="Other Passenger Details", font=("Helvetica", 18)).pack(pady=20)

        #Street address input
        ttk.Label(self, text="Street Address:", font=large_font).pack(pady=2)
        self.street_address = ttk.Entry(self)
        self.street_address.pack(pady=2)

        #City input
        ttk.Label(self, text="City:", font=large_font).pack(pady=2)
        self.city = ttk.Entry(self)
        self.city.pack(pady=2)

        #Country input
        ttk.Label(self, text="Country:", font=large_font).pack(pady=2)
        self.country = ttk.Entry(self)
        self.country.pack(pady=2)

        #Postal code input
        ttk.Label(self, text="Postal Code:", font=large_font).pack(pady=2)
        self.postal_code = ttk.Entry(self)
        self.postal_code.pack(pady=10)

        #Phone number input
        self.phone_label = ttk.Label(self, text="Phone Number:", font=large_font)
        self.phone_label.pack(pady=5)
        self.phone_number = ttk.Entry(self)
        self.phone_number.pack(pady=5)

        #Email address input
        self.email_label = ttk.Label(self, text="Email Address:", font=large_font)
        self.email_label.pack(pady=5)
        self.email_entry = ttk.Entry(self)
        self.email_entry.pack(pady=5)

        ttk.Button(self, text="Proceed to Summary of Booking", command=self.confirm_booking).pack(pady=10)

        ttk.Button(self, text="Back to Credit Card Details", command=lambda: controller.show_frame("CreditCardPage")).pack(pady=(10, 20))

    def confirm_booking(self):
        street = self.street_address.get().title()
        city = self.city.get().title()
        country = self.country.get().title()
        postal = self.postal_code.get()
        phone_number = self.phone_number.get()
        email_address = self.email_entry.get()

        #Check that all fields are filled
        if not (street and city and country and postal and phone_number and email_address):
            messagebox.showwarning("Warning", "Please fill out all fields.")    #Show warning if any field is empty
            return

        #Creates a formatted address
        address = f"{street}, {city}, {country}, {postal}"

        #Store in selected flight's details
        self.controller.selected_flight["address"] = address
        self.controller.selected_flight["phone_number"] = phone_number
        self.controller.selected_flight["email"] = email_address

        #Update confirmation details
        self.controller.frames["ConfirmationPage"].update_confirmation_details()

        self.controller.show_frame("ConfirmationPage")

#Confirmation page class
class ConfirmationPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        controller.display_logo(self)

        ttk.Label(self, text="Summary of Booking", font=("Helvetica", 18)).pack(pady=20)

        #Create a label to display confirmation details
        self.confirmation_label = ttk.Label(self, text="", font=("Helvetica", 14))
        self.confirmation_label.pack(pady=20)

        ttk.Button(self, text="Pay and Confirm Booking", command=self.finish).pack(pady=10)

        ttk.Button(self, text="Back to Other Details", command=lambda: controller.show_frame("OtherDetailsPage")).pack(pady=(5, 20))

    def update_confirmation_details(self):
        selected_flight = self.controller.selected_flight

        #Extract passenger and flight information
        passenger_name = selected_flight.get("passenger_name", "")
        passenger_age = selected_flight.get("passenger_age", "")
        flight_number = selected_flight.get("flight_number", "")
        origin = selected_flight.get("origin", "")
        destination = selected_flight.get("destination", "")
        departure_time = selected_flight.get("departure_time", "")
        arrival_time = selected_flight.get("arrival_time", "")
        flight_date = selected_flight.get("flight_date", "")
        flight_class = selected_flight.get("class", "")
        ticket_type = selected_flight.get("ticket_type", "")
        address = selected_flight.get("address", "")
        phone_number = selected_flight.get("phone_number", "")
        final_price = selected_flight.get("final_price", selected_flight["fare"])

        #Format the confirmation text
        confirmation_text = (
            f"Passenger Name: {passenger_name}\n"
            f"Passenger Age: {passenger_age}\n"
            f"Phone Number: {phone_number}\n"
            f"Address: {address}\n"
            f"Flight Number: {flight_number}\n"
            f"From: {origin} to {destination}\n"
            f"Class: {flight_class}\n"
            f"Ticket Type: {ticket_type}\n"
            f"Departure: {departure_time} on {flight_date}\n"
            f"Total Price: ${final_price:.2f}\n"
        )

        #Update the confirmation label with the formatted text
        self.confirmation_label.config(text=confirmation_text)

    def finish(self):
        #Retrieve selected flight information for booking confirmation
        selected_flight = self.controller.selected_flight

        booking_info = {
            'username': self.controller.current_username,
            "passenger_name": selected_flight.get("passenger_name", ""),
            "passenger_age": selected_flight.get("passenger_age", ""),
            "flight_number": selected_flight.get("flight_number", ""),
            "origin": selected_flight.get("origin", ""),
            "destination": selected_flight.get("destination", ""),
            "departure_time": selected_flight.get("departure_time", ""),
            "arrival_time": selected_flight.get("arrival_time", ""),
            "flight_date": selected_flight.get("flight_date", "").strftime("%Y-%m-%d"),
            "class": selected_flight.get("class", ""),
            "ticket_type": selected_flight.get("ticket_type", ""),
            "address": selected_flight.get("address", ""),
            "phone_number": selected_flight.get("phone_number", ""),
            "email": selected_flight.get("email", ""),
            "fare": selected_flight.get("final_price", selected_flight["fare"])
        }

        #Show a waiting popup while processing the booking
        self.wait_popup = self.show_wait_popup()
        self.controller.save_booking(self.controller.current_username, booking_info)

        #Start a new thread to send the confirmation email and finalize the booking
        threading.Thread(target=self.send_email_and_confirm, args=(booking_info,)).start()

        #Refresh the bookings page
        self.controller.frames["BookingsPage"].display_bookings()


    def show_wait_popup(self):
        #Create a popup window to inform the user that the booking is being confirmed
        wait_popup = tk.Toplevel(self)
        wait_popup.title("Please Wait")

        width = 300
        height = 100
        wait_popup.geometry(f"{width}x{height}")

        screen_width = wait_popup.winfo_screenwidth()
        screen_height = wait_popup.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        wait_popup.geometry(f"{width}x{height}+{x}+{y}")

        label = ttk.Label(wait_popup, text="Confirming booking...\nPlease wait...", padding=10)
        label.pack(expand=True)
        wait_popup.grab_set()   #Make the popup modal
        return wait_popup


    def send_email_and_confirm(self, booking_info):
        # Send confirmation email after the booking has been made
        self.send_confirmation_email(booking_info)

        self.wait_popup.destroy()   #Close the wait popup after email sent

        #Show a message box to user that the booking has been confirmed
        messagebox.showinfo("Booking Confirmed!", "Booking confirmed!\n\nWe have sent a confirmation email to you.\nPlease check your spam inbox.")
        self.controller.show_frame("HomePage")

    def get_base64_image(self, image_path):
        #Convert image to base64-encoded string
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def send_confirmation_email(self, booking_info):
        #Email parameters
        email_sender = 'forflybooking@gmail.com'
        email_password = "onat jemd xyyb vhbq"
        email_receiver = booking_info.get("email")

        #Validate the email address format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email_receiver):
            messagebox.showerror("Error", f"Invalid email address: {email_receiver}")
            return
        
        #Convert images to base64 for embedding
        header_image_base64 = self.get_base64_image('app_files/email_header.png')
        flight_details_icon = self.get_base64_image('app_files/flight_details_icon.png')
        passenger_details_icon = self.get_base64_image('app_files/passenger_details_icon.png')
        total_paid_icon = self.get_base64_image('app_files/total_paid_icon.png')

        #Email subject and body
        subject = 'Your ForFly Booking Confirmation'
        body = f"""
        <html>
        <body>
            <img src="data:image/png;base64,{header_image_base64}" alt="Header Image" style="width:100%; max-width:600px;">
            <p>Dear {booking_info['passenger_name']},</p>

            <p>Your booking to <strong>{booking_info['destination']}</strong> has been confirmed!</p>

            <p>
                <img src="data:image/png;base64,{flight_details_icon}" alt="Flight Details Icon" style="width:40px; vertical-align:middle;">
                <strong><u>Here are your flight details:</u></strong><br>
                From: {booking_info['origin']} to {booking_info['destination']}<br>
                Flight Number: {booking_info['flight_number']}<br>
                Departure: {booking_info['departure_time']} on {booking_info['flight_date']}<br>
                Class: {booking_info['class']}<br>
                Ticket Type: {booking_info['ticket_type']}
            </p>

            <p>
                <img src="data:image/png;base64,{passenger_details_icon}" alt="Passenger Details Icon" style="width:40px; vertical-align:middle;">
                <strong><u>Passenger Details:</u></strong><br>
                Passenger Name: {booking_info['passenger_name']}<br>
                Email: {booking_info['email']}<br>
                Contact Number: {booking_info['phone_number']}
            </p>

            <p>
                <img src="data:image/png;base64,{total_paid_icon}" alt="Total Paid Icon" style="width:40px; vertical-align:middle;">
                <strong>Total Paid: ${booking_info['fare']:.2f}</strong>
            </p>

            <p>Thank you for booking with ForFly, and enjoy your flight!<br>
            The team at ForFly</p>
        </body>
        </html>
        """

        #Sends the email using the SMTP server
        em = EmailMessage()
        em['From'] = email_sender
        em["To"] = email_receiver
        em['Subject'] = subject
        em.add_alternative(body, subtype='html')

        context = ssl.create_default_context()

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender, email_receiver, em.as_string())
        except smtplib.SMTPException as e:
            messagebox.showerror("Error", f"Failed to send email: {str(e)}")

#Starts the application
if __name__ == "__main__":
    app = FlightBookingApp()
    app.mainloop()