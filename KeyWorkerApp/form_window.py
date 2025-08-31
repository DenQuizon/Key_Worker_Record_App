import customtkinter as ctk
from tkcalendar import Calendar 
import datetime
import database_utils as db_manager
from CTkMessagebox import CTkMessagebox
import pdf_generator
from PIL import Image
import os

class FormWindow(ctk.CTkToplevel):
    def __init__(self, parent, service_user_id, service_user_name, dob, month, year, form_data=None, current_user=None):
        super().__init__(parent)
        self.parent = parent 
        self.current_user = current_user
        
        self.service_user_id = service_user_id
        self.service_user_name = service_user_name
        self.dob = dob
        self.month = month
        self.year = year
        self.form_data = form_data
        self.form_id = form_data['id'] if form_data else None

        self.title(f"Key Worker Form - {self.service_user_name} - {month} {year}")
        self.geometry("950x900") 
        self.resizable(False, False) 
        self.grab_set()

        self.main_font = ctk.CTkFont(size=15)
        self.label_font = ctk.CTkFont(size=16, weight="bold")
        self.button_font = ctk.CTkFont(size=15, weight="bold")
        self.icon_font = ctk.CTkFont(size=24)

        # Icon selection tracking
        self.selected_feeling_icons = []
        self.selected_care_icons = []
        self.feeling_icon_buttons = []
        self.care_icon_buttons = []

        self.family_comm_reason_placeholder = "If NO... PLEASE STATE REASON:"
        self.family_comm_issues_placeholder = "ISSUES/CONCERNS/ACTIONS:"

        self._create_header()
        self._create_tabs()
        self._create_main_widgets()
        
        if self.form_data:
            self._load_form_data(self.form_data)
        else:
            self.family_comm_reason_textbox.insert("0.0", self.family_comm_reason_placeholder)
            self.family_comm_issues_textbox.insert("0.0", self.family_comm_issues_placeholder)


    def _create_header(self):
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(padx=20, pady=(20, 10), fill="x")
        header_frame.grid_columnconfigure((1, 3), weight=1)
        
        ctk.CTkLabel(header_frame, text="Service User:", font=self.label_font).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(header_frame, text=self.service_user_name, font=self.main_font).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(header_frame, text="Date of Birth:", font=self.label_font).grid(row=0, column=2, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(header_frame, text=self.dob, font=self.main_font).grid(row=0, column=3, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(header_frame, text="Key Worker:", font=self.label_font).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.key_worker_entry = ctk.CTkEntry(header_frame, placeholder_text="Enter your name", font=self.main_font, height=35)
        self.key_worker_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(header_frame, text="Session Date:", font=self.label_font).grid(row=1, column=2, padx=10, pady=5, sticky="w")
        date_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        date_frame.grid(row=1, column=3, padx=10, pady=5, sticky="ew")
        self.session_day = ctk.CTkOptionMenu(date_frame, values=[f"{d:02d}" for d in range(1,32)], font=self.main_font)
        self.session_month = ctk.CTkOptionMenu(date_frame, values=[d.strftime("%b") for d in [datetime.date(2000, m, 1) for m in range(1,13)]], font=self.main_font)
        self.session_year = ctk.CTkOptionMenu(date_frame, values=[str(y) for y in range(datetime.date.today().year + 2, 2020, -1)], font=self.main_font)
        self.session_day.pack(side="left", padx=2, expand=True, fill="x")
        self.session_month.pack(side="left", padx=2, expand=True, fill="x")
        self.session_year.pack(side="left", padx=2, expand=True, fill="x")
        now = datetime.datetime.now()
        self.session_day.set(now.strftime("%d"))
        self.session_month.set(now.strftime("%b"))
        self.session_year.set(str(now.year))
        self.load_prev_button = ctk.CTkButton(header_frame, text="Load Previous Month's Data", font=self.button_font, command=self._load_previous_month_data)
        self.load_prev_button.grid(row=2, column=0, columnspan=4, padx=10, pady=(10,5), sticky="ew")

    def _create_tabs(self):
        self.tab_view = ctk.CTkTabview(self, width=860)
        self.tab_view.pack(padx=20, pady=10, fill="both", expand=True)
        self.health_tab = self.tab_view.add("My Health")
        self.finances_tab = self.tab_view.add("My Finances")
        self.shopping_tab = self.tab_view.add("Personal Shopping")
        self.plans_tab = self.tab_view.add("Support Plans")
        self.goals_tab = self.tab_view.add("Goals & Feelings")

    def _create_main_widgets(self):
        self.create_health_tab()
        self.create_finances_tab()
        self.create_shopping_tab()
        self.create_support_plans_tab()
        self.create_goals_feelings_tab()
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(padx=20, pady=(10, 20), fill="x")
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.save_button = ctk.CTkButton(button_frame, text="Save Form", font=self.button_font, height=40, command=self.save_form)
        self.save_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.print_button = ctk.CTkButton(button_frame, text="Print to PDF", font=self.button_font, height=40, command=self._print_to_pdf)
        self.print_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.close_button = ctk.CTkButton(button_frame, text="Close Window", font=self.button_font, height=40, fg_color="gray50", command=self.destroy)
        self.close_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    def create_health_tab(self):
        self.appointment_rows = [] 
        main_health_frame = ctk.CTkScrollableFrame(self.health_tab, label_text="Health Details", label_font=self.label_font)
        main_health_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.appointment_frame = ctk.CTkFrame(main_health_frame)
        self.appointment_frame.pack(fill="x", expand=False, padx=10, pady=10)
        self.appointment_frame.grid_columnconfigure((0, 1, 2), weight=1)
        add_appointment_button = ctk.CTkButton(main_health_frame, text="Add New Appointment", command=lambda: self.add_new_appointment_row(), font=self.button_font, height=40)
        add_appointment_button.pack(pady=5, padx=10, fill="x")
        separator = ctk.CTkFrame(main_health_frame, height=2, corner_radius=0); separator.pack(fill="x", padx=10, pady=10)
        questions_frame = ctk.CTkFrame(main_health_frame); questions_frame.pack(fill="x", expand=True, padx=10, pady=10)
        
        # Configure column weights and minimum sizes
        questions_frame.grid_columnconfigure(0, weight=0, minsize=200)  # Labels column
        questions_frame.grid_columnconfigure(1, weight=0, minsize=100)  # Switch column  
        questions_frame.grid_columnconfigure(2, weight=1, minsize=150)  # Date button column
        questions_frame.grid_columnconfigure(3, weight=1, minsize=150)  # Comments column
        ctk.CTkLabel(questions_frame, text="Last Weight:", font=self.main_font).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.weight_entry = ctk.CTkEntry(questions_frame, font=self.main_font, height=35); self.weight_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(questions_frame, text="Last BP:", font=self.main_font).grid(row=0, column=2, padx=(10,5), pady=5, sticky="w")
        self.bp_entry = ctk.CTkEntry(questions_frame, font=self.main_font, height=35); self.bp_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(questions_frame, text="Weight/BP Comments:", font=self.main_font).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.weight_comments_entry = ctk.CTkEntry(questions_frame, font=self.main_font, height=35); self.weight_comments_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(questions_frame, text="Health/Fitness/Diet Concerns?", font=self.main_font).grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.health_concerns_switch = ctk.CTkSwitch(questions_frame, text="No/Yes", onvalue="Yes", offvalue="No", font=self.main_font, width=80); self.health_concerns_switch.grid(row=2, column=1, padx=5, pady=10, sticky="w")
        ctk.CTkLabel(questions_frame, text="Comments:", font=self.main_font).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.health_comments_entry = ctk.CTkEntry(questions_frame, font=self.main_font, height=35); self.health_comments_entry.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        self.nails_date_var = ctk.StringVar(value="Select Date")
        ctk.CTkLabel(questions_frame, text="Needs finger/toe nails cut?", font=self.main_font).grid(row=4, column=0, padx=5, pady=10, sticky="w")
        self.nails_check = ctk.CTkSwitch(questions_frame, text="No/Yes", onvalue="Yes", offvalue="No", font=self.main_font, width=80)
        self.nails_check.grid(row=4, column=1, padx=5, pady=10, sticky="w")
        self.nails_date_button = ctk.CTkButton(
            questions_frame,
            textvariable=self.nails_date_var,
            font=self.main_font,
            height=35,
            command=lambda: self.open_date_picker(self.nails_date_var)
        )
        self.nails_date_button.grid(row=4, column=2, padx=5, pady=5, sticky="ew")
        self.nails_comments_entry = ctk.CTkEntry(questions_frame, placeholder_text="Comments", font=self.main_font, height=35)
        self.nails_comments_entry.grid(row=4, column=3, padx=5, pady=5, sticky="ew")

        self.hair_date_var = ctk.StringVar(value="Select Date")
        ctk.CTkLabel(questions_frame, text="Needs a hair cut?", font=self.main_font).grid(row=5, column=0, padx=5, pady=10, sticky="w")
        self.hair_check = ctk.CTkSwitch(questions_frame, text="No/Yes", onvalue="Yes", offvalue="No", font=self.main_font, width=80)
        self.hair_check.grid(row=5, column=1, padx=5, pady=10, sticky="w")
        self.hair_date_button = ctk.CTkButton(
            questions_frame,
            textvariable=self.hair_date_var,
            font=self.main_font,
            height=35,
            command=lambda: self.open_date_picker(self.hair_date_var)
        )
        self.hair_date_button.grid(row=5, column=2, padx=5, pady=5, sticky="ew")
        self.hair_comments_entry = ctk.CTkEntry(questions_frame, placeholder_text="Comments", font=self.main_font, height=35)
        self.hair_comments_entry.grid(row=5, column=3, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(questions_frame, text="MAR Sheets accurate?", font=self.main_font).grid(row=6, column=0, padx=5, pady=10, sticky="w")
        self.mar_sheets_check = ctk.CTkSwitch(questions_frame, text="No/Yes", onvalue="Yes", offvalue="No", font=self.main_font, width=80)
        self.mar_sheets_check.grid(row=6, column=1, padx=5, pady=10, sticky="w")
        self.mar_sheets_comments_entry = ctk.CTkEntry(questions_frame, placeholder_text="Comments", font=self.main_font, height=35)
        self.mar_sheets_comments_entry.grid(row=6, column=3, padx=5, pady=5, sticky="ew")

    def add_new_appointment_row(self, data=None):
        row_index = len(self.appointment_rows)
        name_entry = ctk.CTkEntry(self.appointment_frame, placeholder_text="Appointment Name", font=self.main_font, height=35)
        last_seen_var = ctk.StringVar(value="Last Seen")
        last_seen_button = ctk.CTkButton(self.appointment_frame, textvariable=last_seen_var, font=self.main_font, height=35, width=120, command=lambda var=last_seen_var: self.open_date_picker(var))
        next_due_var = ctk.StringVar(value="Next Due")
        next_due_button = ctk.CTkButton(self.appointment_frame, textvariable=next_due_var, font=self.main_font, height=35, width=120, command=lambda var=next_due_var: self.open_date_picker(var))
        booked_menu = ctk.CTkOptionMenu(self.appointment_frame, values=["Yes", "No", "N/A"], font=self.main_font, height=35, width=80)
        delete_button = ctk.CTkButton(self.appointment_frame, text="Delete", fg_color="red", hover_color="#c40000", width=80, height=35, font=self.main_font)
        
        name_entry.grid(row=row_index, column=0, padx=5, pady=5, sticky="ew")
        last_seen_button.grid(row=row_index, column=1, padx=5, pady=5, sticky="ew")
        next_due_button.grid(row=row_index, column=2, padx=5, pady=5, sticky="ew")
        booked_menu.grid(row=row_index, column=3, padx=5, pady=5)
        delete_button.grid(row=row_index, column=4, padx=5, pady=5)
        
        row_widgets = (name_entry, last_seen_button, next_due_button, booked_menu, delete_button)
        data_vars = (name_entry, last_seen_var, next_due_var, booked_menu)
        
        def delete_row():
            for widget in row_widgets: widget.destroy()
            self.appointment_rows.remove(data_vars)
            
        delete_button.configure(command=delete_row)
        self.appointment_rows.append(data_vars)
        
        if data:
            name, last_seen, next_due, booked = data
            name_entry.insert(0, name or "")
            last_seen_var.set(last_seen or "Last Seen")
            next_due_var.set(next_due or "Next Due")
            booked_menu.set(booked or "N/A")

    def create_finances_tab(self):
        finances_frame = ctk.CTkFrame(self.finances_tab, fg_color="transparent")
        finances_frame.pack(padx=10, pady=10, fill="both", expand=True)
        grid_frame = ctk.CTkFrame(finances_frame, fg_color="transparent")
        grid_frame.pack(fill="x")
        grid_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(grid_frame, text="How much money do I have in my cash box?", font=self.main_font).grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.finance_cash_box_entry = ctk.CTkEntry(grid_frame, placeholder_text="£", font=self.main_font, height=35)
        self.finance_cash_box_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        ctk.CTkLabel(grid_frame, text="Does it need topping up (above £30.00)?", font=self.main_font).grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.finance_top_up_switch = ctk.CTkSwitch(grid_frame, text="No/Yes", onvalue="Yes", offvalue="No", font=self.main_font, width=80)
        self.finance_top_up_switch.grid(row=1, column=1, padx=5, pady=10, sticky="w")
        ctk.CTkLabel(grid_frame, text="If YES, how much to take out?", font=self.main_font).grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.finance_take_out_entry = ctk.CTkEntry(grid_frame, placeholder_text="£", font=self.main_font, height=35)
        self.finance_take_out_entry.grid(row=2, column=1, padx=5, pady=10, sticky="ew")
        plan_frame = ctk.CTkFrame(grid_frame)
        plan_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=15, sticky="ew")
        plan_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(plan_frame, text="If YES, plan this and enter it into the diary:", font=self.label_font).pack(anchor="w", padx=10, pady=5)
        plan_grid_frame = ctk.CTkFrame(plan_frame, fg_color="transparent")
        plan_grid_frame.pack(fill="x")
        plan_grid_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(plan_grid_frame, text="Date and Time:", font=self.main_font).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.finance_diary_datetime_entry = ctk.CTkEntry(plan_grid_frame, font=self.main_font, height=35)
        self.finance_diary_datetime_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(plan_grid_frame, text="Supporting Staff:", font=self.main_font).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.finance_diary_staff_entry = ctk.CTkEntry(plan_grid_frame, font=self.main_font, height=35)
        self.finance_diary_staff_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

    def create_shopping_tab(self):
        shopping_frame = ctk.CTkFrame(self.shopping_tab, fg_color="transparent")
        shopping_frame.pack(padx=20, pady=20, fill="both", expand=True)
        q_frame = ctk.CTkFrame(shopping_frame)
        q_frame.pack(fill="x")
        
        # Question 1
        q1_frame = ctk.CTkFrame(q_frame)
        q1_frame.pack(fill="x", padx=10, pady=10)
        
        q1_top = ctk.CTkFrame(q1_frame, fg_color="transparent")
        q1_top.pack(fill="x", padx=5, pady=5)
        self.shop_q1_switch = ctk.CTkSwitch(q1_top, text="", onvalue="Yes", offvalue="No", width=60)
        self.shop_q1_switch.pack(side="left", padx=10)
        ctk.CTkLabel(q1_top, text="1) Do I have enough toiletries?", font=self.main_font).pack(side="left", padx=10)
        
        self.shop_q1_comments = ctk.CTkEntry(q1_frame, placeholder_text="Comments", font=self.main_font, height=35)
        self.shop_q1_comments.pack(fill="x", padx=15, pady=(0, 10))
        
        # Question 2
        q2_frame = ctk.CTkFrame(q_frame)
        q2_frame.pack(fill="x", padx=10, pady=10)
        
        q2_top = ctk.CTkFrame(q2_frame, fg_color="transparent")
        q2_top.pack(fill="x", padx=5, pady=5)
        self.shop_q2_switch = ctk.CTkSwitch(q2_top, text="", onvalue="Yes", offvalue="No", width=60)
        self.shop_q2_switch.pack(side="left", padx=10)
        ctk.CTkLabel(q2_top, text="2) Are all my clothes and shoes in good repair?", font=self.main_font).pack(side="left", padx=10)
        
        self.shop_q2_comments = ctk.CTkEntry(q2_frame, placeholder_text="Comments", font=self.main_font, height=35)
        self.shop_q2_comments.pack(fill="x", padx=15, pady=(0, 10))
        
        # Question 3
        q3_frame = ctk.CTkFrame(q_frame)
        q3_frame.pack(fill="x", padx=10, pady=10)
        
        q3_top = ctk.CTkFrame(q3_frame, fg_color="transparent")
        q3_top.pack(fill="x", padx=5, pady=5)
        self.shop_q3_switch = ctk.CTkSwitch(q3_top, text="", onvalue="Yes", offvalue="No", width=60)
        self.shop_q3_switch.pack(side="left", padx=10)
        ctk.CTkLabel(q3_top, text="3) Do I need to or would I like to buy any personal items?", font=self.main_font).pack(side="left", padx=10)
        
        self.shop_q3_comments = ctk.CTkEntry(q3_frame, placeholder_text="Comments", font=self.main_font, height=35)
        self.shop_q3_comments.pack(fill="x", padx=15, pady=(0, 10))
    
    def create_support_plans_tab(self):
        plans_frame = ctk.CTkScrollableFrame(self.plans_tab, label_text="Support Plan Updates", label_font=self.label_font)
        plans_frame.pack(padx=10, pady=10, fill="both", expand=True)
        caredocs_frame = ctk.CTkFrame(plans_frame)
        caredocs_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(caredocs_frame, text="1. MY CAREDOCS SUPPORT PLAN", font=self.label_font).pack(anchor="w", padx=5, pady=5)
        self.caredocs_contacts_switch = ctk.CTkSwitch(caredocs_frame, text="a. Contacts", onvalue="Yes", offvalue="No", font=self.main_font, width=150)
        self.caredocs_contacts_switch.pack(anchor="w", padx=15, pady=5)
        self.caredocs_careplan_switch = ctk.CTkSwitch(caredocs_frame, text="b. Care Plan", onvalue="Yes", offvalue="No", font=self.main_font, width=150)
        self.caredocs_careplan_switch.pack(anchor="w", padx=15, pady=5)
        self.caredocs_meds_switch = ctk.CTkSwitch(caredocs_frame, text="c. Medication", onvalue="Yes", offvalue="No", font=self.main_font, width=150)
        self.caredocs_meds_switch.pack(anchor="w", padx=15, pady=5)
        self.caredocs_bodymap_switch = ctk.CTkSwitch(caredocs_frame, text="d. Body Map", onvalue="Yes", offvalue="No", font=self.main_font, width=150)
        self.caredocs_bodymap_switch.pack(anchor="w", padx=15, pady=5)
        self.caredocs_charts_switch = ctk.CTkSwitch(caredocs_frame, text="e. Charts", onvalue="Yes", offvalue="No", font=self.main_font, width=150)
        self.caredocs_charts_switch.pack(anchor="w", padx=15, pady=5)
        health_plan_frame = ctk.CTkFrame(plans_frame)
        health_plan_frame.pack(fill="x", padx=10, pady=10, expand=True)
        ctk.CTkLabel(health_plan_frame, text="2. MY HEALTH ACTION PLAN/FILE", font=self.label_font).pack(anchor="w", padx=5, pady=5)
        self.health_plan_switch = ctk.CTkSwitch(health_plan_frame, text="Is it up to date?", onvalue="Yes", offvalue="No", font=self.main_font, width=150)
        self.health_plan_switch.pack(anchor="w", padx=15, pady=5)
        actions_frame = ctk.CTkFrame(plans_frame)
        actions_frame.pack(fill="x", padx=10, pady=10, expand=True)
        ctk.CTkLabel(actions_frame, text="If 'NO' to any of the above, what actions are required?", font=self.main_font).pack(anchor="w")
        self.actions_required_textbox = ctk.CTkTextbox(actions_frame, height=80, font=self.main_font)
        self.actions_required_textbox.pack(fill="x", expand=True)
        family_frame = ctk.CTkFrame(plans_frame)
        family_frame.pack(fill="x", padx=10, pady=10, expand=True)
        ctk.CTkLabel(family_frame, text="MONTHLY COMMUNICATION WITH FAMILY/NOK", font=self.label_font).pack(anchor="w", padx=5, pady=5)
        self.family_comm_switch = ctk.CTkSwitch(family_frame, text="Monthly phone call to my family / NOK made?", onvalue="Yes", offvalue="No", font=self.main_font, width=350)
        self.family_comm_switch.pack(anchor="w", padx=15, pady=5)
        self.family_comm_datetime_entry = ctk.CTkEntry(family_frame, placeholder_text="If YES, enter DATE and TIME:", font=self.main_font)
        self.family_comm_datetime_entry.pack(fill="x", padx=15, pady=5)
        self.family_comm_reason_textbox = ctk.CTkTextbox(family_frame, height=60, font=self.main_font)
        self.family_comm_reason_textbox.pack(fill="x", padx=15, pady=5)
        self.family_comm_issues_textbox = ctk.CTkTextbox(family_frame, height=80, font=self.main_font)
        self.family_comm_issues_textbox.pack(fill="x", padx=15, pady=5)

    def create_goals_feelings_tab(self):
        scroll_frame = ctk.CTkScrollableFrame(self.goals_tab, label_text="Monthly Goals and Personal Feelings", label_font=self.label_font)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # HOW ARE YOU FEELING Section with Large Icons
        ctk.CTkLabel(scroll_frame, text="HOW ARE YOU FEELING?", font=self.label_font).pack(anchor="w", padx=10, pady=(5,0))
        
        feeling_main_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        feeling_main_frame.pack(fill="x", padx=10, pady=5)
        
        # Left side: 2x2 Icon Grid (1 inch icons)
        feeling_icon_frame = ctk.CTkFrame(feeling_main_frame, fg_color="transparent", width=180, height=180)
        feeling_icon_frame.pack(side="left", padx=(0, 20), pady=10)
        feeling_icon_frame.pack_propagate(False)
        
        self._create_feeling_icons(feeling_icon_frame)
        
        # Right side: Response text area
        feeling_text_frame = ctk.CTkFrame(feeling_main_frame, fg_color="transparent")
        feeling_text_frame.pack(side="left", fill="both", expand=True)
        
        ctk.CTkLabel(feeling_text_frame, text="Record Response Here:", font=self.main_font).pack(anchor="w", pady=(0,5))
        self.feeling_response_textbox = ctk.CTkTextbox(feeling_text_frame, height=180, font=self.main_font)
        self.feeling_response_textbox.pack(fill="both", expand=True)
        
        # Separator
        ctk.CTkFrame(scroll_frame, height=2, fg_color="gray").pack(fill="x", padx=10, pady=20)
        
        # ARE YOU HAPPY Section with Large Icons
        ctk.CTkLabel(scroll_frame, text="ARE YOU HAPPY WITH YOUR CARE AND SUPPORT?", font=self.label_font).pack(anchor="w", padx=10, pady=(10,0))
        
        care_main_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        care_main_frame.pack(fill="x", padx=10, pady=5)
        
        # Top: Horizontal row of care icons (1 inch icons)
        care_icon_frame = ctk.CTkFrame(care_main_frame, fg_color="transparent", height=90)
        care_icon_frame.pack(fill="x", pady=(0,10))
        care_icon_frame.pack_propagate(False)
        
        self._create_care_icons(care_icon_frame)
        
        # Bottom: Response text area  
        care_text_frame = ctk.CTkFrame(care_main_frame, fg_color="transparent")
        care_text_frame.pack(fill="x")
        
        ctk.CTkLabel(care_text_frame, text="Record Response Here:", font=self.main_font).pack(anchor="w", pady=(0,5))
        self.happy_response_textbox = ctk.CTkTextbox(care_text_frame, height=150, font=self.main_font)
        self.happy_response_textbox.pack(fill="x")
        
        # Separator
        ctk.CTkFrame(scroll_frame, height=2, fg_color="gray").pack(fill="x", padx=10, pady=20)
        
        # GOALS Section (keep existing)
        ctk.CTkLabel(scroll_frame, text="GOALS FOR THIS MONTH", font=self.label_font).pack(anchor="w", padx=10, pady=(10,0))
        ctk.CTkLabel(scroll_frame, text="Identify a GOAL or TARGET or ACHIEVEMENT to work towards or accomplish this month:", font=self.main_font).pack(anchor="w", padx=10, pady=5)
        self.current_goal_textbox = ctk.CTkTextbox(scroll_frame, height=100, font=self.main_font)
        self.current_goal_textbox.pack(fill="x", expand=True, padx=10, pady=5)
        ctk.CTkLabel(scroll_frame, text="Was last month's Goal, Target or Achievement accomplished? If not, why not / progress?", font=self.main_font).pack(anchor="w", padx=10, pady=(10,0))
        self.last_goal_textbox = ctk.CTkTextbox(scroll_frame, height=100, font=self.main_font)
        self.last_goal_textbox.pack(fill="x", expand=True, padx=10, pady=5)
        ctk.CTkLabel(scroll_frame, text="ANY OTHER ACTIONS / NOTES:", font=self.label_font).pack(anchor="w", padx=10, pady=(10,0))
        self.other_notes_textbox = ctk.CTkTextbox(scroll_frame, height=120, font=self.main_font)
        self.other_notes_textbox.pack(fill="x", expand=True, padx=10, pady=5)
    
    def _create_feeling_icons(self, parent_frame):
        """Create 2x2 grid of large feeling icons for residents to point to"""
        # Define icon mappings: filename -> display text
        feeling_icons = [
            ("Happy Emoji.png", "Happy"),
            ("Sad emoji.jpg", "Sad"), 
            ("thumbs up emoji.jpg", "Good"),
            ("thumbds down emoji.png", "Not Good")
        ]
        
        # Create 2x2 grid
        for i, (icon_file, label) in enumerate(feeling_icons):
            row = i // 2
            col = i % 2
            
            icon_path = os.path.join(os.path.dirname(__file__), "images", icon_file)
            
            # Create button frame (1 inch = 72 pixels)
            btn_frame = ctk.CTkFrame(parent_frame, width=72, height=72, fg_color="transparent")
            btn_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            btn_frame.pack_propagate(False)
            
            try:
                # Load and resize image to 1 inch (72 pixels)
                img = Image.open(icon_path)
                img = img.resize((60, 60), Image.Resampling.LANCZOS)
                photo = ctk.CTkImage(light_image=img, dark_image=img, size=(60, 60))
                
                # Create 1-inch clickable button
                btn = ctk.CTkButton(
                    btn_frame, 
                    image=photo,
                    text=label,
                    compound="top",
                    font=("Arial", 8, "bold"),
                    width=72,
                    height=72,
                    fg_color="transparent",
                    hover_color="lightgray",
                    command=lambda label=label: self._select_feeling_icon(label)
                )
                btn.pack(expand=True, fill="both", padx=5, pady=5)
                
                # Store button reference for selection tracking
                self.feeling_icon_buttons.append(btn)
                print(f"Created feeling icon button: {label}")  # Debug print
                
            except Exception as e:
                print(f"Error loading icon {icon_file}: {e}")
                # Fallback text button if image fails
                btn = ctk.CTkButton(
                    btn_frame,
                    text=label,
                    font=("Arial", 10, "bold"),
                    width=72,
                    height=72,
                    fg_color="transparent",
                    hover_color="lightgray",
                    command=lambda label=label: self._select_feeling_icon(label)
                )
                btn.pack(expand=True, fill="both", padx=5, pady=5)
                self.feeling_icon_buttons.append(btn)
        
        # Configure grid weights for proper resizing
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(1, weight=1)
        parent_frame.grid_rowconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(1, weight=1)
    
    def _create_care_icons(self, parent_frame):
        """Create horizontal row of large care icons for residents to point to"""
        # Define care icon mappings: filename -> display text
        care_icons = [
            ("Art Work.jpg", "Art"),
            ("Healthy-Food-Choices.png", "Food"),
            ("Medicine.jpeg", "Medicine"),
            ("Shower.jpg", "Shower"),
            ("Happy Emoji.png", "Happy"),
            ("Sad emoji.jpg", "Sad")
        ]
        
        # Create horizontal row
        for i, (icon_file, label) in enumerate(care_icons):
            icon_path = os.path.join(os.path.dirname(__file__), "images", icon_file)
            
            # Create button frame (1 inch = 72 pixels)
            btn_frame = ctk.CTkFrame(parent_frame, width=72, height=72, fg_color="transparent")
            btn_frame.grid(row=0, column=i, padx=3, pady=5, sticky="nsew")
            btn_frame.pack_propagate(False)
            
            try:
                # Load and resize image to 1 inch
                img = Image.open(icon_path)
                img = img.resize((60, 60), Image.Resampling.LANCZOS)
                photo = ctk.CTkImage(light_image=img, dark_image=img, size=(60, 60))
                
                # Create 1-inch clickable button
                btn = ctk.CTkButton(
                    btn_frame,
                    image=photo,
                    text=label,
                    compound="top",
                    font=("Arial", 8, "bold"),
                    width=72,
                    height=72,
                    fg_color="transparent",
                    hover_color="lightgray",
                    command=lambda label=label: self._select_care_icon(label)
                )
                btn.pack(expand=True, fill="both", padx=2, pady=2)
                
                # Store button reference
                self.care_icon_buttons.append(btn)
                print(f"Created care icon button: {label}")  # Debug print
                
            except Exception as e:
                print(f"Error loading care icon {icon_file}: {e}")
                # Fallback text button
                btn = ctk.CTkButton(
                    btn_frame,
                    text=label,
                    font=("Arial", 10, "bold"),
                    width=72,
                    height=72,
                    fg_color="transparent",
                    hover_color="lightgray",
                    command=lambda label=label: self._select_care_icon(label)
                )
                btn.pack(expand=True, fill="both", padx=2, pady=2)
                self.care_icon_buttons.append(btn)
        
        # Configure grid weights
        for i in range(len(care_icons)):
            parent_frame.grid_columnconfigure(i, weight=1)
        parent_frame.grid_rowconfigure(0, weight=1)
    
    def _select_feeling_icon(self, label):
        """Handle feeling icon selection"""
        print(f"Feeling icon clicked: {label}")  # Debug print
        
        if label in self.selected_feeling_icons:
            self.selected_feeling_icons.remove(label)
        else:
            self.selected_feeling_icons.append(label)
        
        # Update button appearance to show selection
        self._update_feeling_button_colors()
        
        # Add to text area
        try:
            self.feeling_response_textbox.insert("end", f"[{label}] ")
            print(f"Added {label} to feeling textbox")  # Debug print
        except Exception as e:
            print(f"Error adding to feeling textbox: {e}")
    
    def _select_care_icon(self, label):
        """Handle care icon selection"""
        print(f"Care icon clicked: {label}")  # Debug print
        
        if label in self.selected_care_icons:
            self.selected_care_icons.remove(label)
        else:
            self.selected_care_icons.append(label)
        
        # Update button appearance
        self._update_care_button_colors()
        
        # Add to text area
        try:
            self.happy_response_textbox.insert("end", f"[{label}] ")
            print(f"Added {label} to care textbox")  # Debug print
        except Exception as e:
            print(f"Error adding to care textbox: {e}")
    
    def _update_feeling_button_colors(self):
        """Update feeling button colors to show selection state"""
        feeling_labels = ["Happy", "Sad", "Good", "Not Good"]
        for i, btn in enumerate(self.feeling_icon_buttons):
            label = feeling_labels[i]
            if label in self.selected_feeling_icons:
                btn.configure(fg_color="lightgreen", hover_color="green")
            else:
                btn.configure(fg_color="transparent", hover_color="lightgray")
    
    def _update_care_button_colors(self):
        """Update care button colors to show selection state"""
        care_labels = ["Art", "Food", "Medicine", "Shower", "Happy", "Sad"]
        for i, btn in enumerate(self.care_icon_buttons):
            label = care_labels[i]
            if label in self.selected_care_icons:
                btn.configure(fg_color="lightblue", hover_color="blue")
            else:
                btn.configure(fg_color="transparent", hover_color="lightgray")

    def _clear_form(self):
        self.key_worker_entry.delete(0, "end");
        for widget in self.appointment_frame.winfo_children():
            widget.destroy()
        self.appointment_rows.clear()
        
        self.weight_entry.delete(0, "end"); self.bp_entry.delete(0, "end")
        self.weight_comments_entry.delete(0, "end"); self.health_concerns_switch.deselect()
        self.health_comments_entry.delete(0, "end"); self.nails_check.deselect(); self.nails_date_var.set("Select Date")
        self.nails_comments_entry.delete(0, "end")
        self.hair_check.deselect(); self.hair_date_var.set("Select Date"); self.hair_comments_entry.delete(0, "end")
        self.mar_sheets_check.deselect(); self.mar_sheets_comments_entry.delete(0, "end")
        self.finance_cash_box_entry.delete(0, "end"); self.finance_top_up_switch.deselect(); self.finance_take_out_entry.delete(0, "end")
        self.finance_diary_datetime_entry.delete(0, "end"); self.finance_diary_staff_entry.delete(0, "end")
        self.shop_q1_switch.deselect(); self.shop_q1_comments.delete(0, "end")
        self.shop_q2_switch.deselect(); self.shop_q2_comments.delete(0, "end") 
        self.shop_q3_switch.deselect(); self.shop_q3_comments.delete(0, "end")
        self.caredocs_contacts_switch.deselect(); self.caredocs_careplan_switch.deselect(); self.caredocs_meds_switch.deselect()
        self.caredocs_bodymap_switch.deselect(); self.caredocs_charts_switch.deselect(); self.health_plan_switch.deselect()
        
        self.actions_required_textbox.delete("1.0", "end")
        self.family_comm_switch.deselect()
        self.family_comm_datetime_entry.delete(0, "end")
        self.family_comm_reason_textbox.delete("1.0", "end")
        self.family_comm_reason_textbox.insert("0.0", self.family_comm_reason_placeholder)
        self.family_comm_issues_textbox.delete("1.0", "end")
        self.family_comm_issues_textbox.insert("0.0", self.family_comm_issues_placeholder)
        
        self.current_goal_textbox.delete("1.0", "end"); self.last_goal_textbox.delete("1.0", "end"); self.feeling_response_textbox.delete("1.0", "end")
        self.happy_response_textbox.delete("1.0", "end"); self.other_notes_textbox.delete("1.0", "end")

    def _load_previous_month_data(self):
        try:
            current_date = datetime.datetime.strptime(f"01-{self.month}-{self.year}", "%d-%B-%Y")
            prev_month_date = (current_date.replace(day=1) - datetime.timedelta(days=1))
            prev_month_name = prev_month_date.strftime("%B")
            prev_year = str(prev_month_date.year)
            prev_form_month_year = f"{prev_month_name} {prev_year}"
            
            previous_data = db_manager.get_form_data(self.service_user_id, prev_form_month_year)
            
            if previous_data:
                msg = CTkMessagebox(title="Confirm Load", message=f"Found data for {prev_form_month_year}. Load it? This will overwrite unsaved changes.", icon="question", option_1="Cancel", option_2="Load Data")
                if msg.get() == "Load Data": 
                    self._load_form_data(previous_data, carry_over=True)
                    CTkMessagebox(title="Success", message=f"Data from {prev_form_month_year} loaded.", icon="check")
            else: 
                CTkMessagebox(title="No Data Found", message=f"No form data was found for {prev_form_month_year}.", icon="info")
        except ValueError: 
            CTkMessagebox(title="Error", message="Invalid current month or year.", icon="cancel")
            
    def _load_form_data(self, data, carry_over=False):
        self._clear_form()
        form_id_to_load = data.get('id')
        if not form_id_to_load: return

        def _set(widget, value):
            if value is not None:
                widget.delete(0, "end")
                widget.insert(0, str(value))

        def _set_txt(widget, value, placeholder=""):
            widget.delete("1.0", "end")
            if value and str(value).strip() and str(value).strip() != placeholder:
                widget.insert("1.0", value)
            elif placeholder:
                widget.insert("1.0", placeholder)

        def _set_sw(widget, value):
            if value == "Yes":
                widget.select()
            else:
                widget.deselect()

        _set(self.key_worker_entry, data.get('key_worker_name'))
        if not carry_over and data.get('session_datetime'):
            try:
                dt = datetime.datetime.strptime(data['session_datetime'], '%Y-%m-%d')
                self.session_day.set(dt.strftime('%d'))
                self.session_month.set(dt.strftime('%b'))
                self.session_year.set(str(dt.year))
            except (ValueError, TypeError):
                pass

        for appt in db_manager.get_appointments(form_id_to_load):
            self.add_new_appointment_row(data=appt)
        _set(self.weight_entry, data.get('weight'))
        _set(self.bp_entry, data.get('bp'))
        _set(self.weight_comments_entry, data.get('weight_bp_comments'))
        _set_sw(self.health_concerns_switch, data.get('health_concerns'))
        _set(self.health_comments_entry, data.get('health_concerns_comments'))
        _set_sw(self.nails_check, data.get('nails_check'))
        self.nails_date_var.set(data.get('nails_date') or "Select Date")
        _set(self.nails_comments_entry, data.get('nails_comments'))
        _set_sw(self.hair_check, data.get('hair_check'))
        self.hair_date_var.set(data.get('hair_date') or "Select Date")
        _set(self.hair_comments_entry, data.get('hair_comments'))
        _set_sw(self.mar_sheets_check, data.get('mar_sheets_check'))
        _set(self.mar_sheets_comments_entry, data.get('mar_sheets_comments'))

        _set(self.finance_cash_box_entry, data.get('finance_cash_box'))
        _set_sw(self.finance_top_up_switch, data.get('finance_top_up'))
        _set(self.finance_take_out_entry, data.get('finance_take_out'))
        _set(self.finance_diary_datetime_entry, data.get('finance_diary_datetime'))
        _set(self.finance_diary_staff_entry, data.get('finance_diary_staff'))

        _set_sw(self.shop_q1_switch, data.get('shop_q1_toiletries'))
        _set(self.shop_q1_comments, data.get('shop_q1_comments'))
        _set_sw(self.shop_q2_switch, data.get('shop_q2_clothes'))
        _set(self.shop_q2_comments, data.get('shop_q2_comments'))
        _set_sw(self.shop_q3_switch, data.get('shop_q3_personal_items'))
        _set(self.shop_q3_comments, data.get('shop_q3_comments'))

        _set_sw(self.caredocs_contacts_switch, data.get('caredocs_contacts'))
        _set_sw(self.caredocs_careplan_switch, data.get('caredocs_careplan'))
        _set_sw(self.caredocs_meds_switch, data.get('caredocs_meds'))
        _set_sw(self.caredocs_bodymap_switch, data.get('caredocs_bodymap'))
        _set_sw(self.caredocs_charts_switch, data.get('caredocs_charts'))
        _set_sw(self.health_plan_switch, data.get('health_plan_file'))
        _set_txt(self.actions_required_textbox, data.get('actions_required'))
        _set_sw(self.family_comm_switch, data.get('family_comm_made'))
        _set(self.family_comm_datetime_entry, data.get('family_comm_datetime'))
        _set_txt(self.family_comm_reason_textbox, data.get('family_comm_reason'), self.family_comm_reason_placeholder)
        _set_txt(self.family_comm_issues_textbox, data.get('family_comm_issues'), self.family_comm_issues_placeholder)

        if carry_over:
            self.last_goal_textbox.insert("1.0", data.get('current_goal', ''))
        else:
            _set_txt(self.current_goal_textbox, data.get('current_goal'))
            _set_txt(self.last_goal_textbox, data.get('last_goal_progress'))
            _set_txt(self.feeling_response_textbox, data.get('feeling_response'))
            _set_txt(self.happy_response_textbox, data.get('happy_response'))

        _set_txt(self.other_notes_textbox, data.get('other_notes'))

    def open_date_picker(self, date_variable):
        date_picker_win = ctk.CTkToplevel(self)
        date_picker_win.grab_set()
        date_picker_win.title("Select Date")
        date_picker_win.attributes('-topmost', True)
        
        try:
            start_date = datetime.datetime.strptime(date_variable.get(), '%d/%m/%Y')
        except (ValueError, TypeError):
            start_date = datetime.datetime.now()

        picker_width, picker_height = 350, 350
        parent_x, parent_y = self.winfo_x(), self.winfo_y()
        parent_width, parent_height = self.winfo_width(), self.winfo_height()
        center_x = parent_x + (parent_width // 2) - (picker_width // 2)
        center_y = parent_y + (parent_height // 2) - (picker_height // 2)
        date_picker_win.geometry(f"{picker_width}x{picker_height}+{center_x}+{center_y}")
        date_picker_win.resizable(False, False)
        
        cal = Calendar(date_picker_win, selectmode='day', date_pattern='dd/MM/yyyy',
                       year=start_date.year, month=start_date.month, day=start_date.day,
                       font=("Arial", 12), background='white', foreground='black')
        cal.pack(pady=10, padx=10, fill="both", expand=True)
        
        def on_date_select(): 
            date_variable.set(cal.get_date())
            date_picker_win.destroy()
            
        button_frame = ctk.CTkFrame(date_picker_win)
        button_frame.pack(pady=10, padx=10, fill="x")
        
        ok_button = ctk.CTkButton(button_frame, text="OK", command=on_date_select, font=self.button_font, width=100)
        ok_button.pack(side="left", padx=(0,5))
        
        cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=date_picker_win.destroy, font=self.button_font, width=100, fg_color="gray50")
        cancel_button.pack(side="right", padx=(5,0))

    def _get_form_data_as_dict(self):
        session_month_str = self.session_month.get()
        session_month_num = datetime.datetime.strptime(session_month_str, "%b").strftime("%m")
        session_datetime_db = f"{self.session_year.get()}-{session_month_num}-{self.session_day.get()}"
        session_datetime_pdf = f"{self.session_day.get()}/{session_month_num}/{self.session_year.get()}"

        def get_clean_text(textbox, placeholder):
            text = textbox.get("1.0", "end-1c").strip()
            return "" if text == placeholder else text

        def get_clean_date(date_var, default_text):
            date_val = date_var.get()
            return "" if date_val == default_text else date_val

        data = {
            "form_id": self.form_id, "service_user_id": self.service_user_id,
            "service_user_name": self.service_user_name, "dob": self.dob,
            "month": self.month, "year": self.year,
            "form_month_year": f"{self.month} {self.year}",
            "key_worker_name": self.key_worker_entry.get(),
            "session_datetime_db": session_datetime_db,
            "session_datetime": session_datetime_pdf,
            "weight": self.weight_entry.get(), "bp": self.bp_entry.get(),
            "weight_bp_comments": self.weight_comments_entry.get(),
            "health_concerns": self.health_concerns_switch.get(),
            "health_concerns_comments": self.health_comments_entry.get(),
            "nails_check": self.nails_check.get(),
            "nails_date": get_clean_date(self.nails_date_var, "Select Date"),
            "nails_comments": self.nails_comments_entry.get(),
            "hair_check": self.hair_check.get(),
            "hair_date": get_clean_date(self.hair_date_var, "Select Date"),
            "hair_comments": self.hair_comments_entry.get(),
            "mar_sheets_check": self.mar_sheets_check.get(),
            "mar_sheets_comments": self.mar_sheets_comments_entry.get(),
            "finance_cash_box": self.finance_cash_box_entry.get(),
            "finance_top_up": self.finance_top_up_switch.get(),
            "finance_take_out": self.finance_take_out_entry.get(),
            "finance_diary_datetime": self.finance_diary_datetime_entry.get(),
            "finance_diary_staff": self.finance_diary_staff_entry.get(),
            "shop_q1_toiletries": self.shop_q1_switch.get(),
            "shop_q1_comments": self.shop_q1_comments.get(),
            "shop_q2_clothes": self.shop_q2_switch.get(),
            "shop_q2_comments": self.shop_q2_comments.get(),
            "shop_q3_personal_items": self.shop_q3_switch.get(),
            "shop_q3_comments": self.shop_q3_comments.get(),
            "caredocs_contacts": self.caredocs_contacts_switch.get(),
            "caredocs_careplan": self.caredocs_careplan_switch.get(),
            "caredocs_meds": self.caredocs_meds_switch.get(),
            "caredocs_bodymap": self.caredocs_bodymap_switch.get(),
            "caredocs_charts": self.caredocs_charts_switch.get(),
            "health_plan_file": self.health_plan_switch.get(),
            "actions_required": self.actions_required_textbox.get("1.0", "end-1c"),
            "family_comm_made": self.family_comm_switch.get(),
            "family_comm_datetime": self.family_comm_datetime_entry.get(),
            "family_comm_reason": get_clean_text(self.family_comm_reason_textbox, self.family_comm_reason_placeholder),
            "family_comm_issues": get_clean_text(self.family_comm_issues_textbox, self.family_comm_issues_placeholder),
            "current_goal": self.current_goal_textbox.get("1.0", "end-1c"),
            "last_goal_progress": self.last_goal_textbox.get("1.0", "end-1c"),
            "feeling_response": self.feeling_response_textbox.get("1.0", "end-1c"),
            "happy_response": self.happy_response_textbox.get("1.0", "end-1c"),
            "other_notes": self.other_notes_textbox.get("1.0", "end-1c"),
            "feeling_icons_selected": ",".join(self.selected_feeling_icons),
            "care_icons_selected": ",".join(self.selected_care_icons),
            "appointments": []
        }

        for name_entry, last_seen_var, next_due_var, booked_menu in self.appointment_rows:
            if name := name_entry.get():
                data["appointments"].append({
                    "name": name,
                    "last_seen": get_clean_date(last_seen_var, "Last Seen"),
                    "next_due": get_clean_date(next_due_var, "Next Due"),
                    "booked": booked_menu.get()
                })
        return data

    def _print_to_pdf(self):
        self.save_form(show_success_message=False)
        form_data_for_pdf = self._get_form_data_as_dict()
        
        if self.form_id:
            appointments_from_db = db_manager.get_appointments(self.form_id)
            form_data_for_pdf['appointments'] = [
                {'name': a[0], 'last_seen': a[1], 'next_due': a[2], 'booked': a[3]} for a in appointments_from_db
            ]

        success, error_message = pdf_generator.generate_pdf(form_data_for_pdf)
        if success:
            CTkMessagebox(title="Success", message="PDF generated in Downloads and should open automatically.", icon="check")
        else:
            CTkMessagebox(title="PDF Error", message=f"Failed to generate PDF: {error_message}", icon="cancel")

    def save_form(self, show_success_message=True):
        form_data_to_save = self._get_form_data_as_dict()
        db_data = form_data_to_save.copy()
        
        db_data["session_datetime"] = db_data.pop("session_datetime_db")
        appointments_list = db_data.pop('appointments', [])

        saved_form_id = db_manager.save_form_data(db_data, self.current_user['username'])
        
        if saved_form_id:
            self.form_id = saved_form_id 
            
            appointments_for_db = [
                (a['name'], a['last_seen'], a['next_due'], a['booked']) for a in appointments_list
            ]
            db_manager.save_appointments(saved_form_id, appointments_for_db)

            if show_success_message: 
                CTkMessagebox(title="Success", message="Form saved successfully!", icon="check")
        elif show_success_message:
            CTkMessagebox(title="Error", message="There was an error saving the form.", icon="cancel")
