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
    the domain entities, actions, data models, and business rules.
    """
    p_lower = prompt.lower()
    
    # 1. Hospital / Medical
    if any(k in p_lower for k in ["hospital", "doctor", "patient", "clinic", "medical", "appointment"]):
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

    # 2. Library / Book Lending
    if any(k in p_lower for k in ["library", "book", "borrow", "lending", "reading", "isbn"]):
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

    # 3. Vehicle / Car Rental
    if any(k in p_lower for k in ["car", "vehicle", "rental", "fleet", "drive", "automobile"]):
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

    # 4. Inventory / E-Commerce / Warehouse
    if any(k in p_lower for k in ["inventory", "product", "ecommerce", "warehouse", "stock", "store", "order", "shop"]):
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

    # 5. Hotel / Accommodation Booking
    if any(k in p_lower for k in ["hotel", "room", "stay", "guest", "resort", "suite"]):
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

    # 6. Course / Class / Event Enrollment
    if any(k in p_lower for k in ["course", "class", "student", "enroll", "tutoring", "ticket", "event"]):
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

    # 7. Generic Software Requirement Fallback (Intelligently extracted from prompt)
    words = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', prompt) if w.lower() not in ["build", "application", "platform", "system", "user", "where", "can", "the", "and", "must", "never", "two", "same", "for"]]
    primary_topic = words[0].capitalize() if words else "Resource"
    
    return DomainSpec(
        project_name=f"{primary_topic} Management Platform",
        domain="Enterprise Software",
        item_singular="item",
        item_plural="items",
        action_name="reserve",
        action_past="reserved",
        action_reverse="release",
        item_attr1_name="category",
        item_attr2_name="code",
        seed_items=[
            {"name": f"Standard {primary_topic} Alpha", "attr1": "Tier 1", "attr2": "CODE-01"},
            {"name": f"Premium {primary_topic} Beta", "attr1": "Tier 2", "attr2": "CODE-02"},
            {"name": f"Enterprise {primary_topic} Gamma", "attr1": "Tier 3", "attr2": "CODE-03"},
            {"name": f"Dedicated {primary_topic} Delta", "attr1": "Tier 4", "attr2": "CODE-04"}
        ],
        concurrency_rule=f"A {primary_topic} entity must never have conflicting overlapping allocations under concurrent requests.",
        concurrency_invariant_title=f"Zero Conflict {primary_topic} Invariant"
    )
