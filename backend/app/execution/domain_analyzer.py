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
        concurrency_invariant_title: str
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

def analyze_user_prompt(prompt: str) -> DomainSpec:
    """
    Dynamically analyzes any software requirement prompt and synthesizes
    the domain entities, actions, data models, and business rules for diverse projects.
    Uses exact keyword frequency scoring so the most relevant domain is chosen.
    """
    p_lower = prompt.lower()

    domain_keywords = {
        "healthcare": ["hospital", "doctor", "doctors", "patient", "patients", "clinic", "medical", "appointment", "appointments", "dentist", "physician", "health"],
        "education": ["course", "courses", "class", "classes", "enroll", "enrollment", "enrollments", "student", "students", "instructor", "instructors", "curriculum", "syllabus", "academy", "university", "faculty", "tutoring"],
        "library": ["library", "book", "books", "borrow", "borrowed", "lending", "reading", "isbn", "circulation", "author", "authors"],
        "automotive": ["car", "cars", "vehicle", "vehicles", "rental", "fleet", "drive", "automobile", "truck", "suv"],
        "ecommerce": ["inventory", "product", "products", "ecommerce", "warehouse", "stock", "store", "order", "orders", "shop", "checkout", "sku", "oversold"],
        "hospitality": ["hotel", "room", "rooms", "stay", "guest", "guests", "resort", "suite", "suites", "motel", "lodging"],
        "fintech": ["bank", "banking", "fintech", "wallet", "ledger", "account", "accounts", "transfer", "transfers", "deposit", "money", "payment", "payments", "balance", "overdraft"],
        "restaurant": ["restaurant", "table", "tables", "dine", "dining", "bistro", "cafe", "food", "chef", "seating"],
        "aviation": ["flight", "flights", "airline", "airlines", "plane", "aviation", "airport", "boarding", "seat", "seats"],
        "realestate": ["property", "properties", "apartment", "apartments", "real estate", "lease", "tenant", "tenants", "landlord", "realtor", "housing"],
        "fitness": ["gym", "fitness", "workout", "workouts", "trainer", "trainers", "yoga", "crossfit", "pilates", "studio"]
    }

    scores = {d: sum(len(re.findall(rf"\b{re.escape(k)}\b", p_lower)) for k in kws) for d, kws in domain_keywords.items()}
    sorted_domains = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_domain, top_score = sorted_domains[0] if sorted_domains else ("generic", 0)

    if top_score > 0:
        if best_domain == "healthcare":
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
                concurrency_invariant_title="Zero Double-Booking Concurrency Invariant"
            )

        elif best_domain == "education":
            return DomainSpec(
                project_name="Class Enrollment & Registration Platform",
                domain="Higher Education",
                item_singular="course",
                item_plural="courses",
                action_name="enroll",
                action_past="enrolled",
                action_reverse="drop",
                item_attr1_name="instructor",
                item_attr2_name="schedule",
                seed_items=[
                    {"name": "CS101: Distributed Systems", "attr1": "Prof. David Patterson", "attr2": "Mon/Wed 10:00 AM"},
                    {"name": "AI202: Autonomous Agents", "attr1": "Prof. Andrew Ng", "attr2": "Tue/Thu 02:00 PM"},
                    {"name": "MATH301: Cryptography & Security", "attr1": "Prof. Ronald Rivest", "attr2": "Mon/Fri 11:30 AM"},
                    {"name": "SE405: Software Architecture", "attr1": "Prof. Martin Fowler", "attr2": "Wed/Fri 03:00 PM"}
                ],
                concurrency_rule="A course section must never exceed capacity or permit duplicate enrollment seats under concurrent requests.",
                concurrency_invariant_title="Seat Quota & Uniqueness Invariant"
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
                concurrency_invariant_title="Single Borrower Active Copy Invariant"
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
                concurrency_invariant_title="Exclusive Vehicle Lease Invariant"
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
                    {"name": "Custom Mechanical Keyboard", "attr1": "Peripherals", "attr2": "SKU-KB-880"},
                    {"name": "Ultra-Wide 34-inch OLED Monitor", "attr1": "Displays", "attr2": "SKU-MON-34"},
                    {"name": "Ergonomic Mesh Task Chair", "attr1": "Office Furniture", "attr2": "SKU-CHR-01"},
                    {"name": "Active Noise Canceling Headphones", "attr1": "Audio", "attr2": "SKU-AUD-99"}
                ],
                concurrency_rule="A product unit must never be oversold under simultaneous concurrent orders.",
                concurrency_invariant_title="Zero Overselling Inventory Invariant"
            )

        elif best_domain == "hospitality":
            return DomainSpec(
                project_name="Hotel Room Reservation System",
                domain="Hospitality",
                item_singular="room",
                item_plural="rooms",
                action_name="reserve",
                action_past="reserved",
                action_reverse="cancel",
                item_attr1_name="room_type",
                item_attr2_name="floor",
                seed_items=[
                    {"name": "Presidential Oceanfront Suite", "attr1": "Luxury King", "attr2": "Floor 12"},
                    {"name": "Deluxe Executive Room", "attr1": "Double Queen", "attr2": "Floor 8"},
                    {"name": "Skyline Penthouse", "attr1": "Master Suite", "attr2": "Floor 15"},
                    {"name": "Corner Studio Loft", "attr1": "Single King", "attr2": "Floor 5"}
                ],
                concurrency_rule="A room must never be reserved by two guests for the same date range.",
                concurrency_invariant_title="Single Occupant Room Allocation Invariant"
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
                concurrency_invariant_title="Non-Negative Balance & Double-Spend Invariant"
            )

        elif best_domain == "restaurant":
            return DomainSpec(
                project_name="Restaurant Dining & Table Reservation System",
                domain="Food & Hospitality",
                item_singular="table",
                item_plural="tables",
                action_name="reserve",
                action_past="reserved",
                action_reverse="cancel",
                item_attr1_name="section",
                item_attr2_name="capacity",
                seed_items=[
                    {"name": "Terrace View Table 12", "attr1": "Outdoor Garden", "attr2": "4 Guests"},
                    {"name": "Private Dining Suite A", "attr1": "VIP Salon", "attr2": "8 Guests"},
                    {"name": "Chef Counter High-Top 4", "attr1": "Open Kitchen", "attr2": "2 Guests"},
                    {"name": "Main Atrium Table 7", "attr1": "Main Dining Hall", "attr2": "6 Guests"}
                ],
                concurrency_rule="A dining table must never have two guest parties seated for the same seating slot.",
                concurrency_invariant_title="Zero Double-Seating Table Invariant"
            )

        elif best_domain == "aviation":
            return DomainSpec(
                project_name="Airline Flight & Seat Reservation System",
                domain="Aviation & Travel",
                item_singular="flight",
                item_plural="flights",
                action_name="book",
                action_past="booked",
                action_reverse="cancel",
                item_attr1_name="route",
                item_attr2_name="aircraft",
                seed_items=[
                    {"name": "Flight FS-101 (SFO → LHR)", "attr1": "Transatlantic Direct", "attr2": "Boeing 787-9"},
                    {"name": "Flight FS-204 (JFK → NRT)", "attr1": "Pacific Express", "attr2": "Airbus A350-1000"},
                    {"name": "Flight FS-310 (LAX → SYD)", "attr1": "Oceanic Nonstop", "attr2": "Boeing 777-300ER"},
                    {"name": "Flight FS-402 (ORD → FRA)", "attr1": "Continental Route", "attr2": "Airbus A330neo"}
                ],
                concurrency_rule="A flight seat must never be issued to two passengers under concurrent booking requests.",
                concurrency_invariant_title="Single Passenger Seat Invariant"
            )

        elif best_domain == "realestate":
            return DomainSpec(
                project_name="Commercial & Residential Property Leasing System",
                domain="Real Estate",
                item_singular="property",
                item_plural="properties",
                action_name="lease",
                action_past="leased",
                action_reverse="terminate",
                item_attr1_name="property_type",
                item_attr2_name="address",
                seed_items=[
                    {"name": "Hudson Yards Sky Studio", "attr1": "Luxury High-Rise", "attr2": "500 W 33rd St, New York"},
                    {"name": "Pacific Heights Townhouse", "attr1": "Multi-Family Historic", "attr2": "2400 Broadway, San Francisco"},
                    {"name": "River North Creative Loft", "attr1": "Open Commercial Loft", "attr2": "410 N Wells, Chicago"},
                    {"name": "SoHo Retail Flagship", "attr1": "Prime Commercial", "attr2": "92 Prince St, New York"}
                ],
                concurrency_rule="A property unit must never have overlapping active leases under simultaneous execution.",
                concurrency_invariant_title="Exclusive Lease Agreement Invariant"
            )

        elif best_domain == "fitness":
            return DomainSpec(
                project_name="Fitness Studio & Personal Training Scheduler",
                domain="Health & Fitness",
                item_singular="session",
                item_plural="sessions",
                action_name="book",
                action_past="booked",
                action_reverse="cancel",
                item_attr1_name="discipline",
                item_attr2_name="coach",
                seed_items=[
                    {"name": "HIIT Athletic Conditioning", "attr1": "Cardio & Strength", "attr2": "Coach Sarah Jenkins"},
                    {"name": "Ashtanga Core Vinyasa", "attr1": "Mobility Yoga", "attr2": "Guru Arjun Dev"},
                    {"name": "Powerlifting Masterclass", "attr1": "Olympic Weightlifting", "attr2": "Coach Dmitri Volkov"},
                    {"name": "Spin Endurance Interval", "attr1": "Cycle Studio", "attr2": "Coach Mia Zhang"}
                ],
                concurrency_rule="A training slot or class studio spot must never exceed safe member capacity.",
                concurrency_invariant_title="Studio Capacity Limit Invariant"
            )

    # 13. Intelligent Generic NLP Extraction Fallback
    words = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', prompt) if w.lower() not in [
        "build", "application", "platform", "system", "user", "users", "where", "can", "the", "and", "must", "never", "two", "same", "for", "with", "that", "this", "from"
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
        concurrency_invariant_title=f"Zero Conflict {primary_topic} Invariant"
    )
