import tkinter as tk
import json
import os
import re
import datetime
import ssl
import smtplib
import base64
import threading
from tkinter import ttk, messagebox
from datetime import date
from email.message import EmailMessage
from PIL import Image, ImageTk
from tkcalendar import DateEntry
from hashlib import sha256

CREDENTIALS_FILE = "app_files/ver5_credentials/credentials.json"
FLIGHTS_FILE = "app_files/flights.json"
BOOKINGS_FILE = "app_files/bookings.json"
LOGO_PATH = "app_files/forfly_logo.png"

class FlightBookingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ForFly")
        self.geometry("800x600")
        self.center_window()
        
        self.frames = {}
        self.selected_flight = None
        self.load_flights()
        self.username = None
        self.create_frames()
        self.show_frame("LoginPage")

    def center_window(self):
        window_width = 800
        window_height = 700
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')    

    def load_flights(self):
        try:
            with open(FLIGHTS_FILE, "r") as f:
                self.flights = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "Flight data file not found.")
            self.flights = []

    def load_bookings(self, username):
        try:
            with open(BOOKINGS_FILE, "r") as f:
                self.bookings = json.load(f)
                if not isinstance(self.bookings, dict):
                    self.bookings = {}
        except FileNotFoundError:
            self.bookings = {username: []}
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Failed to load bookings: {str(e)}")
            self.bookings = {username: []}


    def save_booking(self, username, booking_info):
        if 'flight_date' in booking_info and isinstance(booking_info['flight_date'], date):
            booking_info['flight_date'] = booking_info['flight_date'].isoformat()

        if username not in self.bookings:
            self.bookings[username] = []

        self.bookings[username].append(booking_info)

        # Saves to JSON file

        with open(BOOKINGS_FILE, "w") as f:
            json.dump(self.bookings, f, indent=4)


    def login(self, username):
        self.current_username = username
        self.load_bookings(username)
        self.show_frame("HomePage")

    def create_frames(self):
        container = ttk.Frame(self)
        container.pack(expand=True, fill='both')

        for F in (LoginPage, RegisterPage, HomePage, SearchFlightsPage, SelectFlightPage, PassengerInfoPage, ConfirmationPage, CreditCardPage, OtherDetailsPage):
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
        elif page_name == "ConfirmationPage":  # Add this line
            frame.update_confirmation_details()

    def display_logo(self, parent):
        logo = Image.open(LOGO_PATH)
        logo = logo.resize((250, 70), Image.LANCZOS)
        logo_image = ImageTk.PhotoImage(logo)
        
        logo_label = ttk.Label(parent, image=logo_image)
        logo_label.image = logo_image
        logo_label.pack(pady=10)


class LoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        controller.display_logo(self)

        ttk.Label(self, text="Login", font=("Helvetica", 16)).pack(pady=20)

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
        hashed_password = sha256(password.encode()).hexdigest()

        try:
            with open(CREDENTIALS_FILE, "r") as f:
                credentials = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "No registered users found.")
            return

        if credentials.get(username) == hashed_password:
            self.controller.current_username = username  #Stores the logged in username
            self.controller.load_bookings(username)  #Loads the user's bookings
            self.controller.show_frame("HomePage")
        else:
            messagebox.showerror("Error", "Invalid credentials.")




class RegisterPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        controller.display_logo(self)

        ttk.Label(self, text="Register", font=("Helvetica", 16)).pack(pady=20)

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
        hashed_password = sha256(password.encode()).hexdigest()

        os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)
        
        try:
            with open(CREDENTIALS_FILE, "r") as f:
                credentials = json.load(f)
        except FileNotFoundError:
            credentials = {}

        if username in credentials:
            messagebox.showerror("Error", "Username already exists.")
            return

        credentials[username] = hashed_password
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump(credentials, f)

        messagebox.showinfo("Success", "Registration successful.")
        self.controller.show_frame("LoginPage")


class HomePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        controller.display_logo(self)

        ttk.Label(self, text="Welcome to the ForFly Flight Booking App!", font=("Helvetica", 16)).pack(pady=20)
        ttk.Label(self, text="What would you like to do today?", font=("Helvetica", 12)).pack(pady=0)

        ttk.Button(self, text="Search Flights", command=lambda: controller.show_frame("SearchFlightsPage")).pack(pady=20)


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

        ttk.Label(self, text="Origin:").pack(pady=5)
        self.origin_combobox = ttk.Combobox(self, textvariable=self.origin, values=self.origins, width=40)
        self.origin_combobox.pack(pady=5)
        self.origin_combobox.bind("<<ComboboxSelected>>", self.update_destinations)

        ttk.Label(self, text="Destination:").pack(pady=5)
        self.destination_combobox = ttk.Combobox(self, textvariable=self.destination, width=40)
        self.destination_combobox.pack(pady=5)
        self.destination_combobox.bind("<<ComboboxSelected>>", self.check_destination)

        ttk.Label(self, text="Departure Date:").pack(pady=5)
        self.depart_date_entry = DateEntry(self, width=40, background='royalblue', foreground='white', borderwidth=2)
        self.depart_date_entry.pack(pady=5)

        self.controller.depart_date = self.depart_date_entry

        ttk.Button(self, text="Search", command=self.search_flights).pack(pady=10)
        ttk.Button(self, text="Back to Home", command=lambda: controller.show_frame("HomePage")).pack(pady=(10, 20))

        self.results_frame = ttk.Frame(self)
        self.results_frame.pack(pady=10)

        self.update_destinations()

    def update_destinations(self, event=None):
        selected_origin = self.origin.get()
        if selected_origin:
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
        selected_destination = self.destination.get()
        if selected_destination == "Please choose an origin first.":
            messagebox.showwarning("Warning", "Please choose an origin first.")
            self.destination_combobox.set('')

    def search_flights(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        origin = self.origin.get()
        destination = self.destination.get()
        depart_date = self.depart_date_entry.get_date() if self.depart_date_entry.get_date() else ""

        if origin == "" or destination == "" or destination == "Please choose an origin first.":
            messagebox.showwarning("Warning", "Please select both origin and destination.")
            return

        results = [flight for flight in self.controller.flights if flight["origin"] == origin and flight["destination"] == destination]

        if not results:
            ttk.Label(self.results_frame, text="No flights found.").pack()
        else:
            for flight in results:
                flight_frame = ttk.Frame(self.results_frame)
                flight_frame.pack(pady=5)

                logo_path = flight["logo"]
                if os.path.isfile(logo_path):
                    logo_image = Image.open(logo_path)
                    logo_image = logo_image.resize((50, 50), Image.LANCZOS)
                    logo_photo = ImageTk.PhotoImage(logo_image)
                    logo_label = ttk.Label(flight_frame, image=logo_photo)
                    logo_label.image = logo_photo
                    logo_label.pack(side=tk.LEFT, padx=10)

                select_button = ttk.Button(flight_frame, text=f"Flight {flight['flight_number']} - from ${flight['price']:.2f}",
                                        command=lambda f=flight: self.select_flight(f))
                select_button.pack(side=tk.LEFT, padx=10)

                details_label = ttk.Label(flight_frame, text=f"Departure: {flight['departure_time']} | "
                                                            f"Arrival: {flight['arrival_time']} | "
                                                            f"Aircraft: {flight['aircraft_model']}")
                details_label.pack(side=tk.LEFT, padx=10)

    def select_flight(self, flight):
        selected_date = self.depart_date_entry.get_date()
        self.controller.selected_flight = flight
        self.controller.selected_flight["flight_date"] = selected_date.strftime("%Y-%m-%d")
        self.controller.selected_flight["fare"] = flight["price"]  # Store the fare
        self.controller.show_frame("SelectFlightPage")
    


class SelectFlightPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        controller.display_logo(self)

        ttk.Label(self, text="Confirm Flight Details and Select Seat Class", font=("Helvetica", 16)).pack(pady=20)

        self.flight_details = tk.StringVar()
        ttk.Label(self, textvariable=self.flight_details).pack(pady=10)

        self.class_selection = tk.StringVar()
        self.ticket_type_selection = tk.StringVar()

        self.class_options = ["First Class", "Business Class", "Premium Economy", "Economy"]
        self.price_multipliers = {"First Class": 3.5, "Business Class": 2.5, "Premium Economy": 1.75, "Economy": 1.0}

        self.ticket_types = ["Child (under 13)", "Adult (13+)"]
        self.ticket_type_multipliers = {"Child (under 13)": 0.5, "Adult (13+)": 1.0}

        self.class_frame = ttk.Frame(self)
        self.class_frame.pack(pady=5)
        
        self.ticket_type_frame = ttk.Frame(self)
        self.ticket_type_frame.pack(pady=5)

        ttk.Label(self.class_frame, text="Select Flight Class", font=("Helvetica", 16)).pack(pady=20)
        ttk.Label(self.ticket_type_frame, text="Select Ticket Type", font=("Helvetica", 16)).pack(pady=20)

        ttk.Button(self, text="Next", command=self.select_class).pack(pady=20)
        
        ttk.Button(self, text="Back", command=self.go_back).pack(pady=10)

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

            # Display flight class options with prices
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


class PassengerInfoPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        controller.display_logo(self)

        ttk.Label(self, text="Passenger Information", font=("Helvetica", 16)).pack(pady=20)

        self.name = tk.StringVar()
        self.age = tk.StringVar()

        ttk.Label(self, text="Name:").pack(pady=5)
        self.name_entry = ttk.Entry(self, textvariable=self.name)
        self.name_entry.pack(pady=5)

        ttk.Label(self, text="Age:").pack(pady=5)
        self.age_entry = ttk.Entry(self, textvariable=self.age)
        self.age_entry.pack(pady=5)

        ttk.Button(self, text="Next", command=self.validate_and_proceed).pack(pady=10)
        ttk.Button(self, text="Back", command=lambda: controller.show_frame("SelectFlightPage")).pack(pady=10)

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

        age = int(age)
        ticket_type = self.controller.selected_flight["ticket_type"]

        if (ticket_type == "Child (under 13)" and age >= 13) or (ticket_type == "Adult (13+)" and age < 13):
            messagebox.showwarning("Warning", f"Age does not match the selected ticket type: {ticket_type}.")
            return

        self.capitalize_and_set_passenger_name()

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

class CreditCardPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        controller.display_logo(self)

        ttk.Label(self, text="Credit Card Details", font=("Helvetica", 16)).pack(pady=(10, 20))

        self.card_number = tk.StringVar()
        self.expiry_month = tk.StringVar()
        self.expiry_year = tk.StringVar()
        self.cvc = tk.StringVar()

        #Card number
        ttk.Label(self, text="Card Number:").pack(pady=(10, 5))
        self.card_entry = ttk.Entry(self, textvariable=self.card_number)
        self.card_entry.pack(pady=(0, 15))
        self.card_entry.bind("<KeyRelease>", self.format_card_number)

        #Card expiry Date
        ttk.Label(self, text="Expiry Date:").pack(pady=(0, 5))

        #Month and year dropdowns
        expiry_frame = ttk.Frame(self)
        expiry_frame.pack(pady=(0, 15))

        # Expiry month
        ttk.Label(expiry_frame, text="Month:").pack(side=tk.LEFT, padx=(0, 5))
        self.expiry_month_menu = ttk.Combobox(expiry_frame, textvariable=self.expiry_month, values=[f"{i:02d}" for i in range(1, 13)], width=5)
        self.expiry_month_menu.pack(side=tk.LEFT, padx=(0, 15))

        #Expiry year
        ttk.Label(expiry_frame, text="Year:").pack(side=tk.LEFT, padx=(0, 5))
        self.expiry_year_menu = ttk.Combobox(expiry_frame, textvariable=self.expiry_year, values=[str(year) for year in range(2024, 2034)], width=8)
        self.expiry_year_menu.pack(side=tk.LEFT)

        #CVC
        ttk.Label(self, text="CVC:").pack(pady=(0, 5))
        self.cvc_entry = ttk.Entry(self, textvariable=self.cvc, show='*')
        self.cvc_entry.pack(pady=(0, 15))
        self.cvc_entry.bind("<KeyRelease>", self.limit_cvc_input)

        ttk.Button(self, text="Next", command=self.validate_and_proceed).pack(pady=(10, 5))
        ttk.Button(self, text="Back", command=lambda: controller.show_frame("PassengerInfoPage")).pack(pady=(15, 20))

    def format_card_number(self, event):
        card_number = self.card_number.get().replace(" ", "")
        if len(card_number) > 16:
            card_number = card_number[:16]
        formatted_number = " ".join(card_number[i:i+4] for i in range(0, len(card_number), 4))
        self.card_number.set(formatted_number)
        self.card_entry.icursor(len(formatted_number))

    def limit_cvc_input(self, event):
        cvc = self.cvc.get()
        if len(cvc) > 4:
            self.cvc.set(cvc[:4])

    def validate_and_proceed(self):
        card_number = self.card_number.get()
        expiry_month = self.expiry_month.get()
        expiry_year = self.expiry_year.get()
        cvc = self.cvc.get()

        if not (card_number and expiry_month and expiry_year and cvc):
            messagebox.showwarning("Warning", "Please enter all credit card details.")
            return

        if not self.validate_card_number(card_number):
            messagebox.showwarning("Warning", "Invalid card number.")
            return

        if not self.validate_expiry_date(expiry_month, expiry_year):
            messagebox.showwarning("Warning", "Invalid expiry date.")
            return

        if not self.validate_cvc(cvc):
            messagebox.showwarning("Warning", "Invalid CVC.")
            return

        self.controller.show_frame("OtherDetailsPage")

    def validate_card_number(self, card_number):
        card_number = card_number.replace(" ", "")
        if not re.match(r"^\d{13,19}$", card_number):
            return False
        return self.luhn_algorithm(card_number)

    def validate_expiry_date(self, month, year):
        if not (re.match(r"^\d{2}$", month) and re.match(r"^\d{4}$", year)):
            return False
        current_date = datetime.datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        expiry_year = int(year)
        expiry_month = int(month)
        if expiry_year < current_year or (expiry_year == current_year and expiry_month < current_month):
            return False
        return True

    def validate_cvc(self, cvc):
        return re.match(r"^\d{3,4}$", cvc) is not None

    def luhn_algorithm(self, card_number):
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

class OtherDetailsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        controller.display_logo(self)

        ttk.Label(self, text="Other Passenger Details", font=("Helvetica", 16)).pack(pady=20)

        ttk.Label(self, text="Street Address:").pack(pady=2)
        self.street_address = ttk.Entry(self)
        self.street_address.pack(pady=2)

        ttk.Label(self, text="City:").pack(pady=2)
        self.city = ttk.Entry(self)
        self.city.pack(pady=2)

        ttk.Label(self, text="Country:").pack(pady=2)
        self.country = ttk.Entry(self)
        self.country.pack(pady=2)

        ttk.Label(self, text="Postal Code:").pack(pady=2)
        self.postal_code = ttk.Entry(self)
        self.postal_code.pack(pady=10)

        self.phone_label = ttk.Label(self, text="Phone Number:")
        self.phone_label.pack(pady=5)
        self.phone_number = ttk.Entry(self)
        self.phone_number.pack(pady=5)

        self.email_label = ttk.Label(self, text="Email Address:")
        self.email_label.pack(pady=5)
        self.email_entry = ttk.Entry(self)
        self.email_entry.pack(pady=5)

        ttk.Button(self, text="Confirm", command=self.confirm_booking).pack(pady=10)

        ttk.Button(self, text="Back", command=lambda: controller.show_frame("CreditCardPage")).pack(pady=(10, 20))

    def confirm_booking(self):
        street = self.street_address.get().title()
        city = self.city.get().title()
        country = self.country.get().title()
        postal = self.postal_code.get()
        phone_number = self.phone_number.get()
        email_address = self.email_entry.get()

        if not (street and city and country and postal and phone_number and email_address):
            messagebox.showwarning("Warning", "Please fill out all fields.")
            return

        address = f"{street}, {city}, {country}, {postal}"

        self.controller.selected_flight["address"] = address
        self.controller.selected_flight["phone_number"] = phone_number
        self.controller.selected_flight["email"] = email_address

        self.controller.frames["ConfirmationPage"].update_confirmation_details()

        self.controller.show_frame("ConfirmationPage")


class ConfirmationPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        controller.display_logo(self)

        ttk.Label(self, text="Summary of Booking", font=("Helvetica", 16)).pack(pady=20)

        self.confirmation_label = ttk.Label(self, text="", font=("Helvetica", 12))
        self.confirmation_label.pack(pady=20)

        ttk.Button(self, text="Confirm Booking", command=self.finish).pack(pady=10)

        ttk.Button(self, text="Back", command=lambda: controller.show_frame("OtherDetailsPage")).pack(pady=(5, 20))

    def update_confirmation_details(self):
        selected_flight = self.controller.selected_flight

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

        self.confirmation_label.config(text=confirmation_text)

    def finish(self):
        selected_flight = self.controller.selected_flight

        # Ensure flight_date is valid
        flight_date = selected_flight.get("flight_date")

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

        self.wait_popup = self.show_wait_popup()
        self.controller.save_booking(self.controller.current_username, booking_info)


        threading.Thread(target=self.send_email_and_confirm, args=(booking_info,)).start()

    def show_wait_popup(self):
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
        wait_popup.grab_set()
        return wait_popup


    def send_email_and_confirm(self, booking_info):
        self.send_confirmation_email(booking_info)

        self.wait_popup.destroy()

        messagebox.showinfo("Booking Confirmed!", "Booking confirmed!\n\nWe have sent a confirmation email to you.\nPlease check your spam inbox.")
        self.controller.show_frame("HomePage")

    def get_base64_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def send_confirmation_email(self, booking_info):
        email_sender = 'forflybooking@gmail.com'
        email_password = "onat jemd xyyb vhbq"
        email_receiver = booking_info.get("email")

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email_receiver):
            messagebox.showerror("Error", f"Invalid email address: {email_receiver}")
            return
        
        header_image_base64 = self.get_base64_image('app_files/email_header.png')
        flight_details_icon = self.get_base64_image('app_files/flight_details_icon.png')
        passenger_details_icon = self.get_base64_image('app_files/passenger_details_icon.png')
        total_paid_icon = self.get_base64_image('app_files/total_paid_icon.png')

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


if __name__ == "__main__":
    app = FlightBookingApp()
    app.mainloop()