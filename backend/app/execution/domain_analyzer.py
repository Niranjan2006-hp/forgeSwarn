import re
from typing import Dict, Any, List

class DomainSpec:
    def __init__(
        self,
        project_name: str,
        domain: str,
        item_singular: str,
        item_plural: str,
        action_name: str,
        action_past: str,
        action_reverse: str,
        item_attr1_name: str,
        item_attr2_name: str,
        seed_items: List[Dict[str, str]],
        concurrency_rule: str,
        concurrency_invariant_title: str,
        ui_type: str = "GENERIC",
        action_label: str = "Submit",
        record_title: str = "My Submitted Records",
        catalog_title: str = "Available Catalog",
        primary_input_label: str = "Notes / Specification",
        primary_input_placeholder: str = "Enter details...",
        selection_label: str = "Selected Item",
        options_label: str = "Select Option / Cohort",
        seed_options: List[str] = None
    ):
        self.project_name = project_name
        self.domain = domain
        self.item_singular = item_singular
        self.item_plural = item_plural
        self.action_name = action_name
        self.action_past = action_past
        self.action_reverse = action_reverse
        self.item_attr1_name = item_attr1_name
        self.item_attr2_name = item_attr2_name
        self.seed_items = seed_items
        self.concurrency_rule = concurrency_rule
        self.concurrency_invariant_title = concurrency_invariant_title
        self.ui_type = ui_type
        self.action_label = action_label
        self.record_title = record_title
        self.catalog_title = catalog_title
        self.primary_input_label = primary_input_label
        self.primary_input_placeholder = primary_input_placeholder
        self.selection_label = selection_label
        self.options_label = options_label
        self.seed_options = seed_options or ["Standard Allocation Tier 1", "Standard Allocation Tier 2", "Standard Allocation Tier 3"]

def analyze_user_prompt(prompt: str) -> DomainSpec:
    """
    Dynamically analyzes any software requirement prompt and synthesizes
    the domain entities, actions, data models, business rules, and UI archetype.
    Robust against typos and tailored for specific engineering domains.
    """
    p_clean = prompt.lower()
    # Normalize common spelling variations and typos
    p_clean = re.sub(r'\bstusent\b', 'student', p_clean)
    p_clean = re.sub(r'\breuirment\b', 'requirement', p_clean)
    p_clean = re.sub(r'\battandance\b', 'attendance', p_clean)
    p_clean = re.sub(r'\battendence\b', 'attendance', p_clean)
    p_clean = re.sub(r'\bmanegement\b', 'management', p_clean)
    p_clean = re.sub(r'\bhospitl\b', 'hospital', p_clean)
    p_clean = re.sub(r'\bdocter\b', 'doctor', p_clean)
    p_clean = re.sub(r'\bvehical\b', 'vehicle', p_clean)
    p_clean = re.sub(r'\bintrenship\b', 'internship', p_clean)

    p_clean = re.sub(r'\bcalculater\b', 'calculator', p_clean)
    p_clean = re.sub(r'\bcalculatr\b', 'calculator', p_clean)
    p_clean = re.sub(r'\bcalcutor\b', 'calculator', p_clean)
    p_clean = re.sub(r'\bclaculator\b', 'calculator', p_clean)

    domain_keywords = {
        "calculator": ["calculator", "calculate", "calc", "scientific calculator", "arithmetic", "math app", "math calculator", "addition", "multiplication", "subtraction", "division", "evaluate math"],
        "todo": ["todo", "todos", "to-do", "to-dos", "task list", "checklist", "notes app", "note taking", "task manager", "todo list"],
        "internship": ["internship", "internships", "intern", "interns", "student internship", "career", "placement", "recruitment", "trainee", "trainees", "apprentice", "apprenticeship", "job opening", "internship opportunities", "manage applications", "apply for internships"],
        "healthcare": ["hospital", "doctor", "doctors", "patient", "patients", "clinic", "medical", "appointment", "appointments", "dentist", "physician", "health"],
        "education": ["course", "courses", "class", "classes", "enroll", "enrollment", "enrollments", "student", "students", "instructor", "instructors", "curriculum", "syllabus", "academy", "university", "faculty", "tutoring"],
        "ecommerce": ["inventory", "product", "products", "ecommerce", "warehouse", "stock", "store", "order", "orders", "shop", "checkout", "sku", "oversold", "retail", "purchase", "purchases", "cart", "catalog"],
        "task": ["task", "tasks", "attendance", "employee", "employees", "shift", "shifts", "project", "projects", "kanban", "ticket", "tickets", "issue", "issues", "timesheet", "work", "staff", "assignee"],
        "library": ["library", "book", "books", "borrow", "borrowed", "lending", "reading", "isbn", "circulation", "author", "authors"],
        "automotive": ["car", "cars", "vehicle", "vehicles", "rental", "fleet", "drive", "automobile", "truck", "suv"],
        "hospitality": ["hotel", "room", "rooms", "stay", "guest", "guests", "resort", "suite", "suites", "motel", "lodging"],
        "fintech": ["bank", "banking", "fintech", "wallet", "ledger", "account", "accounts", "transfer", "transfers", "deposit", "money", "payment", "payments", "balance", "overdraft"],
        "restaurant": ["restaurant", "table", "tables", "dine", "dining", "bistro", "cafe", "food", "chef", "seating"],
        "aviation": ["flight", "flights", "airline", "airlines", "plane", "aviation", "airport", "boarding", "seat", "seats"],
        "realestate": ["property", "properties", "apartment", "apartments", "real estate", "lease", "tenant", "tenants", "landlord", "realtor", "housing"],
        "fitness": ["gym", "fitness", "workout", "workouts", "trainer", "trainers", "yoga", "crossfit", "pilates", "studio"]
    }

    scores = {}
    for d, kws in domain_keywords.items():
        total_hits = 0
        for k in kws:
            total_hits += len(re.findall(rf"\b{re.escape(k)}\b", p_clean))
        scores[d] = total_hits

    sorted_domains = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_domain, top_score = sorted_domains[0] if sorted_domains else ("generic", 0)

    if top_score > 0:
        if best_domain == "calculator":
            return DomainSpec(
                project_name="Scientific & Standard Web Calculator",
                domain="Mathematics & Utilities",
                item_singular="calculation",
                item_plural="calculations",
                action_name="compute",
                action_past="computed",
                action_reverse="clear",
                item_attr1_name="expression",
                item_attr2_name="result",
                seed_items=[
                    {"name": "Standard Arithmetic", "attr1": "128 + 256", "attr2": "384"},
                    {"name": "Exponential Power", "attr1": "2 ** 10", "attr2": "1024"},
                    {"name": "Square Root Extraction", "attr1": "sqrt(65536)", "attr2": "256"},
                    {"name": "Financial Compound Ratio", "attr1": "1500 * 1.085", "attr2": "1627.5"}
                ],
                concurrency_rule="A calculation must safely handle zero-division invariants, prevent server crashes on undefined math operations, and maintain register integrity.",
                concurrency_invariant_title="Zero-Division Safety & Arithmetic Precision Invariant",
                ui_type="CALCULATOR",
                action_label="Execute Calculation",
                record_title="Calculation Tape & History Log",
                catalog_title="Recent Operations & Presets",
                primary_input_label="Mathematical Expression",
                primary_input_placeholder="e.g. (14 * 5) / 2 + sqrt(81)",
                selection_label="Selected Operation",
                options_label="Select Calculation Mode",
                seed_options=[
                    "Standard Precision (10 Decimal Digits)",
                    "Scientific Notation (IEEE-754)",
                    "Financial Rounding (2 Decimal Digits)"
                ]
            )

        elif best_domain == "todo":
            return DomainSpec(
                project_name="Smart Productivity & Task Manager",
                domain="Productivity & Task Management",
                item_singular="task",
                item_plural="tasks",
                action_name="complete",
                action_past="completed",
                action_reverse="reopen",
                item_attr1_name="priority",
                item_attr2_name="due_date",
                seed_items=[
                    {"name": "Review System Architecture Specification", "attr1": "CRITICAL", "attr2": "Today • 05:00 PM"},
                    {"name": "Implement Zero-Division Safety Guards", "attr1": "HIGH", "attr2": "Tomorrow • 10:00 AM"},
                    {"name": "Run End-to-End Regression Verification Suite", "attr1": "HIGH", "attr2": "Friday • 02:00 PM"},
                    {"name": "Publish Release Documentation & API Specs", "attr1": "MEDIUM", "attr2": "Next Monday • 12:00 PM"}
                ],
                concurrency_rule="A task item cannot be duplicated with identical titles under concurrent creation or concurrently modified to conflicting states.",
                concurrency_invariant_title="Task Title Uniqueness & State Integrity Invariant",
                ui_type="TODO",
                action_label="Create New Task",
                record_title="Active Task List & Backlog",
                catalog_title="Task Categories & Priority Boards",
                primary_input_label="Task Title & Detailed Description",
                primary_input_placeholder="e.g. Conduct security vulnerability assessment...",
                selection_label="Selected Task",
                options_label="Select Task Priority",
                seed_options=[
                    "CRITICAL Priority (Immediate Action)",
                    "HIGH Priority (Sprint Target)",
                    "MEDIUM Priority (Standard Backlog)",
                    "LOW Priority (Nice to Have)"
                ]
            )

        elif best_domain == "internship":
            return DomainSpec(
                project_name="Student Internship & Career Placement Portal",
                domain="Higher Education & Career Services",
                item_singular="internship",
                item_plural="internships",
                action_name="apply",
                action_past="applied",
                action_reverse="withdraw",
                item_attr1_name="company",
                item_attr2_name="role_details",
                seed_items=[
                    {"name": "Cloud Systems & Infrastructure Intern", "attr1": "Google Cloud", "attr2": "Full-Time Summer • $52/hr • Mountain View / Remote"},
                    {"name": "Autonomous AI Research Intern", "attr1": "DeepMind", "attr2": "Research Track • $55/hr • London / Mountain View"},
                    {"name": "Full-Stack Web Engineering Intern", "attr1": "Vercel & Next.js", "attr2": "Software Team • $48/hr • Remote"},
                    {"name": "Security & Cryptography Intern", "attr1": "Cloudflare", "attr2": "Systems Track • $50/hr • Austin / Remote"}
                ],
                concurrency_rule="A student cannot submit duplicate active applications for the same internship opening simultaneously, and an opening cannot exceed its maximum applicant quota under concurrent submissions.",
                concurrency_invariant_title="Duplicate Application & Candidate Quota Invariant",
                ui_type="APPLICATION",
                action_label="Submit Application",
                record_title="My Submitted Internship Applications",
                catalog_title="Available Internship Opportunities & Job Postings",
                primary_input_label="Student Profile, Resume / Portfolio URL & Statement of Interest",
                primary_input_placeholder="CS Senior (GPA 3.8) • github.com/student • Excited to contribute to cloud distributed systems!",
                selection_label="Selected Internship Opportunity",
                options_label="Select Internship Cohort / Term",
                seed_options=[
                    "Summer 2026 Cohort (Full-Time • 12 Weeks)",
                    "Fall 2026 Cohort (Co-op • 16 Weeks)",
                    "Spring 2027 Cohort (Part-Time • 12 Weeks)"
                ]
            )

        elif best_domain == "healthcare":
            return DomainSpec(
                project_name="Hospital Appointment Management System",
                domain="Healthcare",
                item_singular="doctor",
                item_plural="doctors",
                action_name="book",
                action_past="booked",
                action_reverse="cancel",
                item_attr1_name="specialty",
                item_attr2_name="room",
                seed_items=[
                    {"name": "Dr. Priya Sharma", "attr1": "Cardiology", "attr2": "Suite 301"},
                    {"name": "Dr. Marcus Vance", "attr1": "Neurology", "attr2": "Suite 405"},
                    {"name": "Dr. Elena Rostova", "attr1": "Pediatrics", "attr2": "Suite 102"},
                    {"name": "Dr. James Wilson", "attr1": "Orthopedics", "attr2": "Suite 204"}
                ],
                concurrency_rule="A doctor must never have two patients booked for the same time slot.",
                concurrency_invariant_title="Zero Double-Booking Concurrency Invariant",
                ui_type="RESERVATION",
                action_label="Confirm Appointment Booking",
                record_title="My Scheduled Medical Appointments",
                catalog_title="Specialist Physicians & Doctors Directory",
                primary_input_label="Consultation Reason & Chief Symptoms",
                primary_input_placeholder="Routine cardiovascular follow-up checkup",
                selection_label="Selected Physician",
                options_label="Select Consultation Time Slot",
                seed_options=[
                    "2026-10-15 Slot 1 (09:00 AM)",
                    "2026-10-15 Slot 2 (10:30 AM)",
                    "2026-10-15 Slot 3 (02:00 PM)",
                    "2026-10-15 Slot 4 (03:30 PM)"
                ]
            )

        elif best_domain == "ecommerce":
            return DomainSpec(
                project_name="Inventory & Order Fulfillment System",
                domain="Supply Chain & E-Commerce",
                item_singular="product",
                item_plural="products",
                action_name="order",
                action_past="ordered",
                action_reverse="cancel",
                item_attr1_name="category",
                item_attr2_name="sku",
                seed_items=[
                    {"name": "Custom Mechanical Keyboard", "attr1": "Peripherals", "attr2": "SKU-KB-880 • $149"},
                    {"name": "Ultra-Wide 34-inch OLED Monitor", "attr1": "Displays", "attr2": "SKU-MON-34 • $799"},
                    {"name": "Ergonomic Mesh Task Chair", "attr1": "Office Furniture", "attr2": "SKU-CHR-01 • $320"},
                    {"name": "Active Noise Canceling Headphones", "attr1": "Audio", "attr2": "SKU-AUD-99 • $249"}
                ],
                concurrency_rule="A product unit must never be oversold or decremented below zero under simultaneous concurrent orders.",
                concurrency_invariant_title="Zero Overselling Inventory Invariant",
                ui_type="ORDER",
                action_label="Place & Confirm Order",
                record_title="My Orders & Shipping History",
                catalog_title="Product Catalog & In-Stock Inventory",
                primary_input_label="Order Quantity & Shipping Delivery Address",
                primary_input_placeholder="Qty: 1 • 742 Evergreen Terrace, Springfield, OR 97477",
                selection_label="Selected Product Item",
                options_label="Select Shipping Speed",
                seed_options=[
                    "Standard Ground Delivery (3-5 Days)",
                    "Express Priority Air Dispatch (1-2 Days)",
                    "Same-Day Urgent Courier"
                ]
            )

        elif best_domain == "education":
            return DomainSpec(
                project_name="Class Enrollment & Course Registration Platform",
                domain="Higher Education",
                item_singular="course",
                item_plural="courses",
                action_name="enroll",
                action_past="enrolled",
                action_reverse="drop",
                item_attr1_name="instructor",
                item_attr2_name="schedule",
                seed_items=[
                    {"name": "CS101: Distributed Systems", "attr1": "Prof. David Patterson", "attr2": "Mon/Wed 10:00 AM • 4 Credits"},
                    {"name": "AI202: Autonomous Agents", "attr1": "Prof. Andrew Ng", "attr2": "Tue/Thu 02:00 PM • 3 Credits"},
                    {"name": "MATH301: Cryptography & Security", "attr1": "Prof. Ronald Rivest", "attr2": "Mon/Fri 11:30 AM • 4 Credits"},
                    {"name": "SE405: Software Architecture", "attr1": "Prof. Martin Fowler", "attr2": "Wed/Fri 03:00 PM • 3 Credits"}
                ],
                concurrency_rule="A course section must never exceed seat capacity or permit duplicate enrollment seats under concurrent requests.",
                concurrency_invariant_title="Seat Quota & Uniqueness Invariant",
                ui_type="ENROLLMENT",
                action_label="Register & Enroll in Course",
                record_title="My Enrolled Courses & Study Plan",
                catalog_title="Academic Course Catalog & Class Sections",
                primary_input_label="Student ID, Degree Major & Academic Standing",
                primary_input_placeholder="Student ID: STU-8921 • B.S. Computer Science • Senior",
                selection_label="Selected Course Offering",
                options_label="Select Section & Schedule",
                seed_options=[
                    "Section 01 (Mon/Wed 10:00 AM - In Person)",
                    "Section 02 (Tue/Thu 02:00 PM - In Person)",
                    "Section 03 (Mon/Fri 11:30 AM - Hybrid)"
                ]
            )

        elif best_domain == "task":
            return DomainSpec(
                project_name="Team Task & Attendance Operations System",
                domain="Operations & Workforce Management",
                item_singular="task",
                item_plural="tasks",
                action_name="claim",
                action_past="claimed",
                action_reverse="release",
                item_attr1_name="team",
                item_attr2_name="priority",
                seed_items=[
                    {"name": "Core Authentication Gateway Token Refresh", "attr1": "Backend Infrastructure", "attr2": "Priority: CRITICAL"},
                    {"name": "Real-Time Student Application Pipeline Sync", "attr1": "Product Engineering", "attr2": "Priority: HIGH"},
                    {"name": "Automated Shift Attendance Verification", "attr1": "Operations Team", "attr2": "Priority: MEDIUM"},
                    {"name": "Database ACID Index Optimization", "attr1": "Data Reliability", "attr2": "Priority: HIGH"}
                ],
                concurrency_rule="A task or shift cannot be concurrently claimed or modified by multiple team members under simultaneous race conditions.",
                concurrency_invariant_title="Atomic Task Assignment Invariant",
                ui_type="TASK",
                action_label="Claim & Assign Work Item",
                record_title="My Assigned Work Items & Tickets",
                catalog_title="Active Sprint Work Items & Tasks",
                primary_input_label="Assignee Hours Estimate, Notes & Implementation Approach",
                primary_input_placeholder="Assignee: Lead Engineer • Est: 4h • Sprint 14 Milestone",
                selection_label="Selected Work Item",
                options_label="Select Sprint Allocation Queue",
                seed_options=[
                    "Sprint 14 Queue (Active Milestone)",
                    "Sprint 15 Queue (Upcoming Backlog)",
                    "Hotfix & Escalation Track"
                ]
            )

        elif best_domain == "fintech":
            return DomainSpec(
                project_name="Digital Financial Settlement Ledger",
                domain="Fintech & Banking",
                item_singular="account",
                item_plural="accounts",
                action_name="transfer",
                action_past="transferred",
                action_reverse="reverse",
                item_attr1_name="account_type",
                item_attr2_name="routing_code",
                seed_items=[
                    {"name": "Prime Operating Account", "attr1": "Checking", "attr2": "ROUT-001-NYC"},
                    {"name": "High Yield Treasury Vault", "attr1": "Savings", "attr2": "ROUT-002-LDN"},
                    {"name": "Merchant Settlement Escrow", "attr1": "Escrow", "attr2": "ROUT-003-SFO"},
                    {"name": "Institutional Liquidity Pool", "attr1": "Commercial", "attr2": "ROUT-004-TYO"}
                ],
                concurrency_rule="An account balance must never overdraft or permit conflicting simultaneous debit allocations.",
                concurrency_invariant_title="Non-Negative Balance & Double-Spend Invariant",
                ui_type="FINANCE",
                action_label="Execute Balance Transfer",
                record_title="Settlement Ledger & Transfer History",
                catalog_title="Destination Accounts & Corporate Ledgers",
                primary_input_label="Transfer Amount ($ USD) & Settlement Memo",
                primary_input_placeholder="$1,500.00 USD • Invoice #9021 Vendor Settlement",
                selection_label="Selected Settlement Account",
                options_label="Select Settlement Method",
                seed_options=[
                    "Instant ACH Settlement (Real-Time)",
                    "Wire Transfer Express (Gross Settlement)",
                    "Scheduled Batch Liquidity Clear"
                ]
            )

        elif best_domain == "automotive":
            return DomainSpec(
                project_name="Fleet Vehicle Rental & Reservation System",
                domain="Automotive & Transportation",
                item_singular="vehicle",
                item_plural="vehicles",
                action_name="reserve",
                action_past="reserved",
                action_reverse="cancel",
                item_attr1_name="model",
                item_attr2_name="license_plate",
                seed_items=[
                    {"name": "Tesla Model 3 Dual Motor", "attr1": "Electric Sedan", "attr2": "CA-7EV901"},
                    {"name": "BMW 330i M-Sport", "attr1": "Executive Sedan", "attr2": "NY-4BM202"},
                    {"name": "Toyota RAV4 Hybrid", "attr1": "Compact SUV", "attr2": "TX-9TR441"},
                    {"name": "Ford F-150 Lightning", "attr1": "Electric Pickup", "attr2": "WA-3FL819"}
                ],
                concurrency_rule="A vehicle must never be reserved by two drivers for overlapping reservation periods.",
                concurrency_invariant_title="Exclusive Vehicle Lease Invariant",
                ui_type="RESERVATION",
                action_label="Confirm Vehicle Reservation",
                record_title="My Active Vehicle Rentals",
                catalog_title="Fleet Vehicles Available for Reservation",
                primary_input_label="Pickup Date, Rental Duration & Driver License No",
                primary_input_placeholder="Pickup: 2026-10-15 • 3 Days • DL: C4819201",
                selection_label="Selected Fleet Vehicle",
                options_label="Select Rental Time Window",
                seed_options=[
                    "Weekend Getaway (Fri 09:00 AM - Sun 06:00 PM)",
                    "Weekly Business Commute (Mon - Fri)",
                    "Daily Standard Rental (24h Window)"
                ]
            )

        elif best_domain == "library":
            return DomainSpec(
                project_name="Library Book Lending & Circulation System",
                domain="Education & Library Science",
                item_singular="book",
                item_plural="books",
                action_name="borrow",
                action_past="borrowed",
                action_reverse="return",
                item_attr1_name="author",
                item_attr2_name="isbn",
                seed_items=[
                    {"name": "Clean Code", "attr1": "Robert C. Martin", "attr2": "978-0132350884"},
                    {"name": "Designing Data-Intensive Applications", "attr1": "Martin Kleppmann", "attr2": "978-1449373320"},
                    {"name": "The Pragmatic Programmer", "attr1": "David Thomas, Andrew Hunt", "attr2": "978-0135957059"},
                    {"name": "Introduction to Algorithms", "attr1": "Thomas H. Cormen", "attr2": "978-0262033848"}
                ],
                concurrency_rule="A book copy must never be loaned to two members at the same time.",
                concurrency_invariant_title="Single Borrower Active Copy Invariant",
                ui_type="LOAN",
                action_label="Borrow Book Copy",
                record_title="My Borrowed Books & Active Loans",
                catalog_title="Library Catalog & Available Volumes",
                primary_input_label="Member Card Number & Loan Purpose",
                primary_input_placeholder="Member ID: LIB-49201 • Academic Research Loan",
                selection_label="Selected Volume",
                options_label="Select Loan Duration Period",
                seed_options=[
                    "Standard 14-Day Borrowing Period",
                    "Extended 30-Day Research Loan",
                    "Semester Course Reserve Loan"
                ]
            )

    # Intelligent Generic NLP Extraction Fallback
    words = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', prompt) if w.lower() not in [
        "build", "application", "platform", "system", "user", "users", "where", "can", "the", "and", "must", "never", "two", "same", "for", "with", "that", "this", "from", "allows", "manage"
    ]]
    primary_topic = words[0].capitalize() if words else "Resource"
    
    return DomainSpec(
        project_name=f"{primary_topic} Management System",
        domain=f"{primary_topic} Operations",
        item_singular=primary_topic.lower(),
        item_plural=f"{primary_topic.lower()}s",
        action_name="allocate",
        action_past="allocated",
        action_reverse="release",
        item_attr1_name="category",
        item_attr2_name="identifier",
        seed_items=[
            {"name": f"{primary_topic} Alpha Pro", "attr1": "Enterprise Grade", "attr2": f"{primary_topic[:3].upper()}-001"},
            {"name": f"{primary_topic} Beta Matrix", "attr1": "High Availability", "attr2": f"{primary_topic[:3].upper()}-002"},
            {"name": f"{primary_topic} Gamma Core", "attr1": "Standard Tier", "attr2": f"{primary_topic[:3].upper()}-003"},
            {"name": f"{primary_topic} Delta Dynamic", "attr1": "Premium Cluster", "attr2": f"{primary_topic[:3].upper()}-004"}
        ],
        concurrency_rule=f"A {primary_topic.lower()} must never be concurrently claimed by two users for the same allocation slot.",
        concurrency_invariant_title=f"Zero Conflict {primary_topic} Invariant",
        ui_type="GENERIC",
        action_label=f"Confirm {primary_topic} Allocation",
        record_title=f"My Active {primary_topic} Records",
        catalog_title=f"Available {primary_topic} Catalog",
        primary_input_label="Allocation Notes, Specification & Purpose",
        primary_input_placeholder="Enter operational specification...",
        selection_label=f"Selected {primary_topic}",
        options_label="Select Allocation Option",
        seed_options=[
            "Tier 1 Allocation Window",
            "Tier 2 Allocation Window",
            "Tier 3 Allocation Window"
        ]
    )
