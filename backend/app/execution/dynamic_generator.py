import logging
from typing import List, Dict, Any
from app.execution.workspace import ProjectWorkspace
from app.execution.domain_analyzer import analyze_user_prompt, DomainSpec

logger = logging.getLogger("forgeswarm.dynamic_generator")

class DynamicCodeGenerator:
    @classmethod
    def generate_calculator_project(cls, workspace: ProjectWorkspace, spec: DomainSpec, has_bug: bool = True) -> List[str]:
        # 1. requirements.txt
        workspace.write_file("requirements.txt", """fastapi>=0.115.0
uvicorn[standard]>=0.32.0
sqlalchemy>=2.0.35
pydantic>=2.9.0
pytest>=8.3.0
httpx>=0.27.0
""")

        # 2. Dockerfile
        workspace.write_file("Dockerfile", """FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8005
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005"]
""")

        # 3. app/database.py
        workspace.write_file("app/database.py", """from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./app_calculator.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""")

        # 4. app/models.py
        workspace.write_file("app/models.py", """from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base

class Calculation(Base):
    __tablename__ = "calculations"
    id = Column(Integer, primary_key=True, index=True)
    expression = Column(String(255), nullable=False)
    result = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class MemoryRegister(Base):
    __tablename__ = "memory_registers"
    id = Column(Integer, primary_key=True, index=True)
    register_name = Column(String(50), default="M", unique=True)
    value = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow)
""")

        # 5. app/services/calculator_service.py
        if has_bug:
            zero_div_block = """        if op_type is ast.Div:
            # VULNERABILITY (BR-001 VIOLATION): Missing zero-division check
            # Executing raw division raises unhandled ZeroDivisionError (HTTP 500)
            return left / right"""
        else:
            zero_div_block = """        if op_type is ast.Div:
            # REPAIRED (BR-001): Zero-Division Safety Guard prevents 500 server crash
            if right == 0:
                raise HTTPException(status_code=400, detail="Cannot divide by zero")
            return left / right"""

        service_code = f"""import ast
import operator
import math
from fastapi import HTTPException

_OPERATORS = {{
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
    ast.Mod: operator.mod,
}}

_FUNCTIONS = {{
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log10,
    "ln": math.log,
    "abs": abs,
}}

def _eval_node(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise HTTPException(status_code=400, detail="Invalid numeric constant in expression")
    elif isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        op_type = type(node.op)
{zero_div_block}
        if op_type in _OPERATORS:
            return _OPERATORS[op_type](left, right)
        raise HTTPException(status_code=400, detail="Unsupported arithmetic operator")
    elif isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand)
        op_type = type(node.op)
        if op_type in _OPERATORS:
            return _OPERATORS[op_type](operand)
        raise HTTPException(status_code=400, detail="Unsupported unary operator")
    elif isinstance(node, ast.Call):
        func_name = node.func.id if isinstance(node.func, ast.Name) else ""
        if func_name in _FUNCTIONS:
            args = [_eval_node(arg) for arg in node.args]
            return _FUNCTIONS[func_name](*args)
        raise HTTPException(status_code=400, detail=f"Unsupported function: {{func_name}}")
    elif isinstance(node, ast.Name):
        if node.id.lower() == "pi":
            return math.pi
        elif node.id.lower() == "e":
            return math.e
        raise HTTPException(status_code=400, detail=f"Unknown identifier: {{node.id}}")
    else:
        raise HTTPException(status_code=400, detail="Unsupported expression syntax")

def evaluate_calculation(raw_expr: str) -> float:
    if not raw_expr or not raw_expr.strip():
        raise HTTPException(status_code=400, detail="Expression cannot be empty")
    
    expr = raw_expr.strip()
    if len(expr) > 255:
        raise HTTPException(status_code=400, detail="Expression exceeds maximum character limit")

    # Defense against code injection
    if any(keyword in expr.lower() for keyword in ["__", "import", "eval", "exec", "open", "os", "sys", "subprocess", "lambda", "class"]):
        raise HTTPException(status_code=400, detail="Malicious expression detected: code execution prohibited")

    # Normalize symbols:
    expr = expr.replace("×", "*").replace("÷", "/").replace("−", "-").replace("^", "**")
    expr = expr.replace("%", " * 0.01")

    try:
        parsed = ast.parse(expr, mode='eval')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Syntax error in mathematical expression: {{str(e)}}")

    result = _eval_node(parsed.body)
    if math.isnan(result) or math.isinf(result):
        raise HTTPException(status_code=400, detail="Calculation resulted in undefined numeric overflow")

    return result
"""
        workspace.write_file("app/services/calculator_service.py", service_code)

        # 6. app/main.py
        main_code = """from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.models import Calculation, MemoryRegister
from app.services.calculator_service import evaluate_calculation

# Initialize tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Scientific & Standard Web Calculator",
    version="1.0.0",
    description="Engineered by ForgeSwarm Autonomous AI Engineering Swarm"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def seed_calculator():
    db = next(get_db())
    if db.query(MemoryRegister).count() == 0:
        db.add(MemoryRegister(register_name="M", value=0.0))
        db.commit()
    if db.query(Calculation).count() == 0:
        db.add_all([
            Calculation(expression="128 + 256", result="384"),
            Calculation(expression="2 ** 10", result="1024"),
            Calculation(expression="sqrt(65536)", result="256"),
        ])
        db.commit()
    db.close()

seed_calculator()

class CalculateRequest(BaseModel):
    expression: str

class MemoryRequest(BaseModel):
    action: str
    value: Optional[float] = 0.0

@app.post("/api/calculate")
def calculate_endpoint(req: CalculateRequest, db: Session = Depends(get_db)):
    val = evaluate_calculation(req.expression)
    if val.is_integer():
        formatted = str(int(val))
    else:
        formatted = f"{round(val, 10):g}"
    
    calc = Calculation(expression=req.expression, result=formatted)
    db.add(calc)
    db.commit()
    db.refresh(calc)
    return {
        "id": calc.id,
        "expression": req.expression,
        "result": val,
        "formatted_result": formatted
    }

@app.get("/api/history")
def get_history(db: Session = Depends(get_db)):
    calcs = db.query(Calculation).order_by(Calculation.id.desc()).limit(50).all()
    return [{
        "id": c.id,
        "expression": c.expression,
        "result": c.result,
        "created_at": c.created_at.strftime("%H:%M:%S") if c.created_at else ""
    } for c in calcs]

@app.delete("/api/history")
def clear_history(db: Session = Depends(get_db)):
    db.query(Calculation).delete()
    db.commit()
    return {"status": "SUCCESS", "message": "Calculation history tape cleared"}

@app.get("/api/memory")
def get_memory(db: Session = Depends(get_db)):
    mem = db.query(MemoryRegister).filter(MemoryRegister.register_name == "M").first()
    return {"value": mem.value if mem else 0.0}

@app.post("/api/memory")
def update_memory(req: MemoryRequest, db: Session = Depends(get_db)):
    mem = db.query(MemoryRegister).filter(MemoryRegister.register_name == "M").first()
    if not mem:
        mem = MemoryRegister(register_name="M", value=0.0)
        db.add(mem)
    
    act = req.action.lower()
    if act == "store":
        mem.value = req.value or 0.0
    elif act == "add":
        mem.value += (req.value or 0.0)
    elif act == "subtract":
        mem.value -= (req.value or 0.0)
    elif act == "clear":
        mem.value = 0.0
    else:
        raise HTTPException(status_code=400, detail=f"Unknown memory action: {req.action}")
    
    db.commit()
    db.refresh(mem)
    return {"status": "SUCCESS", "value": mem.value}

@app.get("/health")
def health():
    return {"status": "HEALTHY", "app": "Scientific & Standard Web Calculator", "engine": "FastAPI + Python Math AST"}

@app.get("/", response_class=HTMLResponse)
def index():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ForgeSwarm • Operating Web Calculator</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap');
    body { font-family: 'Inter', sans-serif; }
    .mono { font-family: 'JetBrains Mono', monospace; }
  </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col items-center justify-center p-4">
  <div class="w-full max-w-4xl bg-slate-900/90 border border-slate-800 rounded-3xl shadow-2xl p-6 backdrop-blur-xl">
    <!-- Header -->
    <div class="flex flex-wrap items-center justify-between pb-5 border-b border-slate-800 mb-6 gap-3">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center font-bold text-white shadow-lg shadow-emerald-500/20">
          ±
        </div>
        <div>
          <h1 class="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            ForgeSwarm Calculator
            <span class="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-full font-medium">Live API</span>
          </h1>
          <p class="text-xs text-slate-400">Autonomous Engineering Generated Web Utility</p>
        </div>
      </div>
      <div class="flex items-center space-x-2">
        <span id="mem-badge" class="mono text-xs px-2.5 py-1 bg-indigo-950/60 text-indigo-300 border border-indigo-800/50 rounded-lg">M: 0</span>
        <button onclick="clearHistory()" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg border border-slate-700 transition">Clear Tape</button>
      </div>
    </div>

    <!-- Main Grid: Calculator Left, Tape Right -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <!-- Calculator Body -->
      <div class="lg:col-span-7 bg-slate-950 border border-slate-800 rounded-2xl p-5 shadow-inner">
        <!-- Dual Display Screen -->
        <div class="bg-slate-900 border border-slate-800/80 rounded-xl p-4 mb-4">
          <div id="expr-display" class="mono text-sm text-slate-400 h-6 text-right overflow-x-auto whitespace-nowrap"></div>
          <div id="main-display" class="mono text-4xl sm:text-5xl font-bold text-emerald-400 text-right overflow-x-auto whitespace-nowrap select-all tracking-tight py-1">0</div>
          <div id="err-banner" class="hidden text-xs text-rose-400 font-mono text-right mt-1 font-semibold"></div>
        </div>

        <!-- Memory Buttons -->
        <div class="grid grid-cols-5 gap-2 mb-3">
          <button onclick="handleMemory('clear')" class="py-1.5 text-xs font-mono font-semibold bg-slate-900 hover:bg-slate-800 text-slate-400 rounded-lg border border-slate-800 transition active:scale-95">MC</button>
          <button onclick="handleMemory('recall')" class="py-1.5 text-xs font-mono font-semibold bg-slate-900 hover:bg-slate-800 text-slate-300 rounded-lg border border-slate-800 transition active:scale-95">MR</button>
          <button onclick="handleMemory('add')" class="py-1.5 text-xs font-mono font-semibold bg-slate-900 hover:bg-slate-800 text-indigo-400 rounded-lg border border-slate-800 transition active:scale-95">M+</button>
          <button onclick="handleMemory('subtract')" class="py-1.5 text-xs font-mono font-semibold bg-slate-900 hover:bg-slate-800 text-indigo-400 rounded-lg border border-slate-800 transition active:scale-95">M-</button>
          <button onclick="handleMemory('store')" class="py-1.5 text-xs font-mono font-semibold bg-slate-900 hover:bg-slate-800 text-indigo-300 rounded-lg border border-slate-800 transition active:scale-95">MS</button>
        </div>

        <!-- Scientific Ribbon -->
        <div class="grid grid-cols-6 gap-2 mb-3">
          <button onclick="appendFunction('sqrt(')" class="py-2 text-xs font-mono bg-slate-900/80 hover:bg-slate-800 text-teal-400 rounded-lg border border-slate-800 transition">√x</button>
          <button onclick="appendOperator('**2')" class="py-2 text-xs font-mono bg-slate-900/80 hover:bg-slate-800 text-teal-400 rounded-lg border border-slate-800 transition">x²</button>
          <button onclick="appendOperator('**')" class="py-2 text-xs font-mono bg-slate-900/80 hover:bg-slate-800 text-teal-400 rounded-lg border border-slate-800 transition">xʸ</button>
          <button onclick="appendPercentage()" class="py-2 text-xs font-mono bg-slate-900/80 hover:bg-slate-800 text-teal-400 rounded-lg border border-slate-800 transition">%</button>
          <button onclick="appendConstant('pi')" class="py-2 text-xs font-mono bg-slate-900/80 hover:bg-slate-800 text-teal-400 rounded-lg border border-slate-800 transition">π</button>
          <button onclick="toggleSign()" class="py-2 text-xs font-mono bg-slate-900/80 hover:bg-slate-800 text-teal-400 rounded-lg border border-slate-800 transition">±</button>
        </div>

        <!-- Keypad Grid -->
        <div class="grid grid-cols-4 gap-2.5">
          <!-- Row 1 -->
          <button onclick="clearAll()" class="py-3.5 text-sm font-bold bg-rose-950/40 hover:bg-rose-900/60 text-rose-300 border border-rose-800/40 rounded-xl transition active:scale-95">C</button>
          <button onclick="clearEntry()" class="py-3.5 text-sm font-semibold bg-slate-800/60 hover:bg-slate-800 text-slate-300 border border-slate-700/60 rounded-xl transition active:scale-95">CE</button>
          <button onclick="deleteDigit()" class="py-3.5 text-sm font-semibold bg-slate-800/60 hover:bg-slate-800 text-slate-300 border border-slate-700/60 rounded-xl transition active:scale-95">DEL</button>
          <button onclick="appendOperator('/')" class="py-3.5 text-lg font-bold bg-amber-950/40 hover:bg-amber-900/60 text-amber-400 border border-amber-800/40 rounded-xl transition active:scale-95">÷</button>

          <!-- Row 2 -->
          <button onclick="appendDigit('7')" class="py-3.5 text-lg font-mono font-semibold bg-slate-900 hover:bg-slate-800 text-white border border-slate-800 rounded-xl transition active:scale-95">7</button>
          <button onclick="appendDigit('8')" class="py-3.5 text-lg font-mono font-semibold bg-slate-900 hover:bg-slate-800 text-white border border-slate-800 rounded-xl transition active:scale-95">8</button>
          <button onclick="appendDigit('9')" class="py-3.5 text-lg font-mono font-semibold bg-slate-900 hover:bg-slate-800 text-white border border-slate-800 rounded-xl transition active:scale-95">9</button>
          <button onclick="appendOperator('*')" class="py-3.5 text-lg font-bold bg-amber-950/40 hover:bg-amber-900/60 text-amber-400 border border-amber-800/40 rounded-xl transition active:scale-95">×</button>

          <!-- Row 3 -->
          <button onclick="appendDigit('4')" class="py-3.5 text-lg font-mono font-semibold bg-slate-900 hover:bg-slate-800 text-white border border-slate-800 rounded-xl transition active:scale-95">4</button>
          <button onclick="appendDigit('5')" class="py-3.5 text-lg font-mono font-semibold bg-slate-900 hover:bg-slate-800 text-white border border-slate-800 rounded-xl transition active:scale-95">5</button>
          <button onclick="appendDigit('6')" class="py-3.5 text-lg font-mono font-semibold bg-slate-900 hover:bg-slate-800 text-white border border-slate-800 rounded-xl transition active:scale-95">6</button>
          <button onclick="appendOperator('-')" class="py-3.5 text-lg font-bold bg-amber-950/40 hover:bg-amber-900/60 text-amber-400 border border-amber-800/40 rounded-xl transition active:scale-95">−</button>

          <!-- Row 4 -->
          <button onclick="appendDigit('1')" class="py-3.5 text-lg font-mono font-semibold bg-slate-900 hover:bg-slate-800 text-white border border-slate-800 rounded-xl transition active:scale-95">1</button>
          <button onclick="appendDigit('2')" class="py-3.5 text-lg font-mono font-semibold bg-slate-900 hover:bg-slate-800 text-white border border-slate-800 rounded-xl transition active:scale-95">2</button>
          <button onclick="appendDigit('3')" class="py-3.5 text-lg font-mono font-semibold bg-slate-900 hover:bg-slate-800 text-white border border-slate-800 rounded-xl transition active:scale-95">3</button>
          <button onclick="appendOperator('+')" class="py-3.5 text-lg font-bold bg-amber-950/40 hover:bg-amber-900/60 text-amber-400 border border-amber-800/40 rounded-xl transition active:scale-95">+</button>

          <!-- Row 5 -->
          <button onclick="appendDigit('(')" class="py-3.5 text-base font-mono bg-slate-900 hover:bg-slate-800 text-slate-400 border border-slate-800 rounded-xl transition active:scale-95">(</button>
          <button onclick="appendDigit('0')" class="py-3.5 text-lg font-mono font-semibold bg-slate-900 hover:bg-slate-800 text-white border border-slate-800 rounded-xl transition active:scale-95">0</button>
          <button onclick="appendDigit('.')" class="py-3.5 text-lg font-mono font-semibold bg-slate-900 hover:bg-slate-800 text-white border border-slate-800 rounded-xl transition active:scale-95">.</button>
          <button onclick="calculate()" class="py-3.5 text-xl font-bold bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl shadow-lg shadow-emerald-600/30 transition active:scale-95">=</button>
        </div>
      </div>

      <!-- Calculation Tape / History -->
      <div class="lg:col-span-5 bg-slate-950 border border-slate-800 rounded-2xl p-5 flex flex-col shadow-inner">
        <div class="flex items-center justify-between pb-3 border-b border-slate-800/80 mb-3">
          <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">Audit Calculation Tape</span>
          <span class="text-xs text-slate-500 font-mono">SQLite Persistent</span>
        </div>
        <div id="tape-list" class="flex-1 space-y-2 overflow-y-auto max-h-[360px] pr-1">
          <!-- Dynamic history items loaded via JS -->
        </div>
      </div>
    </div>
  </div>

  <script>
    let currentInput = "0";
    let expressionTrace = "";
    let shouldResetDisplay = false;

    const mainDisplay = document.getElementById("main-display");
    const exprDisplay = document.getElementById("expr-display");
    const errBanner = document.getElementById("err-banner");
    const memBadge = document.getElementById("mem-badge");
    const tapeList = document.getElementById("tape-list");

    function updateDisplay() {
      mainDisplay.innerText = currentInput;
      exprDisplay.innerText = expressionTrace;
    }

    function clearError() {
      errBanner.classList.add("hidden");
      errBanner.innerText = "";
    }

    function showError(msg) {
      errBanner.innerText = msg;
      errBanner.classList.remove("hidden");
    }

    function appendDigit(d) {
      clearError();
      if (currentInput === "0" || shouldResetDisplay) {
        currentInput = d;
        shouldResetDisplay = false;
      } else {
        currentInput += d;
      }
      updateDisplay();
    }

    function appendOperator(op) {
      clearError();
      expressionTrace += " " + currentInput + " " + op;
      shouldResetDisplay = true;
      updateDisplay();
    }

    function appendFunction(fn) {
      clearError();
      expressionTrace += " " + fn;
      shouldResetDisplay = true;
      updateDisplay();
    }

    function appendPercentage() {
      clearError();
      currentInput += "%";
      updateDisplay();
    }

    function appendConstant(c) {
      clearError();
      currentInput = c;
      shouldResetDisplay = false;
      updateDisplay();
    }

    function toggleSign() {
      if (currentInput.startsWith("-")) {
        currentInput = currentInput.slice(1);
      } else if (currentInput !== "0") {
        currentInput = "-" + currentInput;
      }
      updateDisplay();
    }

    function deleteDigit() {
      clearError();
      if (currentInput.length > 1) {
        currentInput = currentInput.slice(0, -1);
      } else {
        currentInput = "0";
      }
      updateDisplay();
    }

    function clearEntry() {
      clearError();
      currentInput = "0";
      updateDisplay();
    }

    function clearAll() {
      clearError();
      currentInput = "0";
      expressionTrace = "";
      updateDisplay();
    }

    async function calculate() {
      clearError();
      const fullExpr = (expressionTrace + " " + currentInput).trim();
      if (!fullExpr) return;

      try {
        const res = await fetch("/api/calculate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ expression: fullExpr })
        });
        const data = await res.json();
        if (res.ok) {
          expressionTrace = fullExpr + " =";
          currentInput = data.formatted_result;
          shouldResetDisplay = true;
          updateDisplay();
          loadHistory();
        } else {
          showError(data.detail || "Calculation error");
          currentInput = "Error";
          updateDisplay();
        }
      } catch (err) {
        showError("Network / Server connection error");
      }
    }

    async function handleMemory(act) {
      try {
        let val = parseFloat(currentInput) || 0;
        let body = { action: act, value: val };
        if (act === "recall") {
          const res = await fetch("/api/memory");
          const data = await res.json();
          currentInput = String(data.value);
          shouldResetDisplay = true;
          updateDisplay();
          return;
        }
        const res = await fetch("/api/memory", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body)
        });
        const data = await res.json();
        memBadge.innerText = "M: " + data.value;
      } catch (e) {
        showError("Memory register fault");
      }
    }

    async function loadHistory() {
      try {
        const res = await fetch("/api/history");
        const list = await res.json();
        tapeList.innerHTML = "";
        list.forEach(item => {
          const div = document.createElement("div");
          div.className = "p-2.5 rounded-lg bg-slate-900 hover:bg-slate-850 border border-slate-800/80 cursor-pointer transition flex items-center justify-between";
          div.onclick = () => {
            currentInput = item.result;
            shouldResetDisplay = true;
            updateDisplay();
          };
          div.innerHTML = `
            <div>
              <div class="mono text-xs text-slate-400">${item.expression}</div>
              <div class="mono text-sm font-bold text-emerald-400">= ${item.result}</div>
            </div>
            <span class="text-[10px] text-slate-500 font-mono">${item.created_at || ""}</span>
          `;
          tapeList.appendChild(div);
        });
      } catch (e) {}
    }

    async function clearHistory() {
      await fetch("/api/history", { method: "DELETE" });
      loadHistory();
    }

    // Keyboard listener
    window.addEventListener("keydown", (e) => {
      if (e.key >= "0" && e.key <= "9") appendDigit(e.key);
      else if (e.key === ".") appendDigit(".");
      else if (e.key === "+") appendOperator("+");
      else if (e.key === "-") appendOperator("-");
      else if (e.key === "*") appendOperator("*");
      else if (e.key === "/") { e.preventDefault(); appendOperator("/"); }
      else if (e.key === "Enter" || e.key === "=") { e.preventDefault(); calculate(); }
      else if (e.key === "Backspace") deleteDigit();
      else if (e.key === "Escape") clearAll();
    });

    loadHistory();
  </script>
</body>
</html>'''
"""
        workspace.write_file("app/main.py", main_code)

        # 7. tests/test_suite.py
        test_code = """import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# --- FR-001: Standard Arithmetic Operations ---
def test_fr_001_addition():
    resp = client.post("/api/calculate", json={"expression": "128 + 256"})
    assert resp.status_code == 200
    assert resp.json()["result"] == 384.0

def test_fr_001_subtraction():
    resp = client.post("/api/calculate", json={"expression": "500 - 116"})
    assert resp.status_code == 200
    assert resp.json()["result"] == 384.0

def test_fr_001_multiplication():
    resp = client.post("/api/calculate", json={"expression": "16 * 24"})
    assert resp.status_code == 200
    assert resp.json()["result"] == 384.0

def test_fr_001_standard_division():
    resp = client.post("/api/calculate", json={"expression": "1920 / 5"})
    assert resp.status_code == 200
    assert resp.json()["result"] == 384.0

def test_fr_001_order_of_operations():
    resp = client.post("/api/calculate", json={"expression": "10 + 20 * 3"})
    assert resp.status_code == 200
    assert resp.json()["result"] == 70.0

# --- FR-002: Advanced & Scientific Functions ---
def test_fr_002_square_root():
    resp = client.post("/api/calculate", json={"expression": "sqrt(144)"})
    assert resp.status_code == 200
    assert resp.json()["result"] == 12.0

def test_fr_002_power_exponentiation():
    resp = client.post("/api/calculate", json={"expression": "2 ** 10"})
    assert resp.status_code == 200
    assert resp.json()["result"] == 1024.0

def test_fr_002_percentage_calculation():
    resp = client.post("/api/calculate", json={"expression": "500 * 20%"})
    assert resp.status_code == 200
    assert resp.json()["result"] == 100.0

# --- FR-003: LCD Display Formatting ---
def test_fr_003_lcd_display_formatting():
    resp = client.post("/api/calculate", json={"expression": "0.1 + 0.2"})
    assert resp.status_code == 200
    assert resp.json()["formatted_result"] == "0.3"

# --- FR-004: Memory Registers ---
def test_fr_004_memory_store_and_recall():
    resp1 = client.post("/api/memory", json={"action": "store", "value": 42.0})
    assert resp1.status_code == 200
    assert resp1.json()["value"] == 42.0

    resp2 = client.get("/api/memory")
    assert resp2.status_code == 200
    assert resp2.json()["value"] == 42.0

def test_fr_004_memory_add_subtract():
    client.post("/api/memory", json={"action": "store", "value": 10.0})
    resp1 = client.post("/api/memory", json={"action": "add", "value": 15.0})
    assert resp1.status_code == 200
    assert resp1.json()["value"] == 25.0

    resp2 = client.post("/api/memory", json={"action": "subtract", "value": 5.0})
    assert resp2.status_code == 200
    assert resp2.json()["value"] == 20.0

def test_fr_004_memory_clear():
    resp = client.post("/api/memory", json={"action": "clear"})
    assert resp.status_code == 200
    assert resp.json()["value"] == 0.0

# --- FR-005: Calculation Tape & History ---
def test_fr_005_calculation_history_persistence():
    client.post("/api/calculate", json={"expression": "99 + 1"})
    resp = client.get("/api/history")
    assert resp.status_code == 200
    history = resp.json()
    assert len(history) > 0
    assert any(h["expression"] == "99 + 1" for h in history)

def test_fr_005_calculation_history_clear():
    del_resp = client.delete("/api/history")
    assert del_resp.status_code == 200
    get_resp = client.get("/api/history")
    assert len(get_resp.json()) == 0

# --- SEC-001: Injection Defense ---
def test_sec_001_expression_injection_defense():
    resp = client.post("/api/calculate", json={"expression": "__import__('os').system('ls')"})
    assert resp.status_code == 400

# --- NFR-001: System Health ---
def test_nfr_001_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "HEALTHY"

# --- BR-001: Zero-Division Safety Invariant ---
def test_br_001_zero_division_prevention():
    \"\"\"
    BR-001 SAFETY INVARIANT:
    Division by zero must return HTTP 400 Bad Request with 'Cannot divide by zero',
    and NEVER crash with HTTP 500 or unhandled server error.
    \"\"\"
    resp = client.post("/api/calculate", json={"expression": "10 / 0"})
    assert resp.status_code == 400, f"Expected 400 Bad Request for zero division, got {resp.status_code}"
    assert "cannot divide by zero" in resp.json().get("detail", "").lower()
"""
        workspace.write_file("tests/test_suite.py", test_code)
        return workspace.list_files()

    @classmethod
    def generate_project(cls, workspace: ProjectWorkspace, user_requirement: str, has_bug: bool = True) -> List[str]:
        """
        Dynamically generates a full-stack application (FastAPI + SQLAlchemy + UI + Pytest Suite)
        tailored directly to the user's software requirement and domain.
        """
        workspace.initialize()
        spec: DomainSpec = analyze_user_prompt(user_requirement)

        if spec.ui_type == "CALCULATOR":
            return cls.generate_calculator_project(workspace, spec, has_bug)

        item_cls = spec.item_singular.capitalize()
        alloc_cls = f"{item_cls}Allocation"
        
        # 1. requirements.txt
        workspace.write_file("requirements.txt", """fastapi>=0.115.0
uvicorn[standard]>=0.32.0
sqlalchemy>=2.0.35
pydantic>=2.9.0
pytest>=8.3.0
httpx>=0.27.0
""")

        # 2. Dockerfile
        workspace.write_file("Dockerfile", """FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8005
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005"]
""")

        # 3. app/database.py
        workspace.write_file("app/database.py", f"""from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./app_{spec.item_singular}.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={{"check_same_thread": False}}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""")

        # 4. app/models.py
        if not has_bug:
            table_args_str = f"__table_args__ = (UniqueConstraint('{spec.item_singular}_id', 'slot_time', name='uix_{spec.item_singular}_slot'),)"
            constraint_import = "from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint"
        else:
            table_args_str = "__table_args__ = ()"
            constraint_import = "from sqlalchemy import Column, Integer, String, DateTime, ForeignKey"

        workspace.write_file("app/models.py", f"""{constraint_import}
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="MEMBER")
    is_active = Column(String(10), default="TRUE")
    created_at = Column(DateTime, default=datetime.utcnow)
    allocations = relationship("{alloc_cls}", back_populates="user")

class {item_cls}(Base):
    __tablename__ = "{spec.item_plural}"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    {spec.item_attr1_name} = Column(String(100), nullable=False)
    {spec.item_attr2_name} = Column(String(100), nullable=False)
    status = Column(String(50), default="AVAILABLE")
    created_at = Column(DateTime, default=datetime.utcnow)
    allocations = relationship("{alloc_cls}", back_populates="{spec.item_singular}")

class {alloc_cls}(Base):
    __tablename__ = "allocations"
    id = Column(Integer, primary_key=True, index=True)
    {spec.item_singular}_id = Column(Integer, ForeignKey("{spec.item_plural}.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    slot_time = Column(String(50), nullable=False)
    notes = Column(String(255), default="Standard allocation")
    status = Column(String(50), default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)

    {spec.item_singular} = relationship("{item_cls}", back_populates="allocations")
    user = relationship("User", back_populates="allocations")
    {table_args_str}

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False)
    entity_name = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=True)
    details = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
""")

        # 5. app/services/allocation_service.py
        if has_bug:
            service_code = f"""import time
import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import {alloc_cls}

logger = logging.getLogger("allocation_service")

def execute_allocation(db: Session, {spec.item_singular}_id: int, user_id: int, slot_time: str, notes: str):
    # VULNERABILITY (BR-001 VIOLATION): TOCTOU Race Condition
    # Check availability without atomic row lock or DB unique constraint
    existing = db.query({alloc_cls}).filter(
        {alloc_cls}.{spec.item_singular}_id == {spec.item_singular}_id,
        {alloc_cls}.slot_time == slot_time,
        {alloc_cls}.status == "ACTIVE"
    ).first()
    
    if existing:
        raise HTTPException(status_code=409, detail="{item_cls} slot already allocated")
        
    # Simulated IO latency allows interleaved concurrent execution
    time.sleep(0.04)
    
    record = {alloc_cls}(
        {spec.item_singular}_id={spec.item_singular}_id,
        user_id=user_id,
        slot_time=slot_time,
        notes=notes,
        status="ACTIVE"
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
"""
        else:
            service_code = f"""import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.models import {alloc_cls}

logger = logging.getLogger("allocation_service")

# Thread-safe in-memory reservation lock for ACID concurrency invariant
import threading
_allocation_lock = threading.Lock()

def execute_allocation(db: Session, {spec.item_singular}_id: int, user_id: int, slot_time: str, notes: str):
    # REPAIRED: Atomic synchronization and uniqueness protection against race conditions
    with _allocation_lock:
        existing = db.query({alloc_cls}).filter(
            {alloc_cls}.{spec.item_singular}_id == {spec.item_singular}_id,
            {alloc_cls}.slot_time == slot_time,
            {alloc_cls}.status == "ACTIVE"
        ).first()
        
        if existing:
            raise HTTPException(status_code=409, detail="{item_cls} slot already allocated")
            
        try:
            record = {alloc_cls}(
                {spec.item_singular}_id={spec.item_singular}_id,
                user_id=user_id,
                slot_time=slot_time,
                notes=notes,
                status="ACTIVE"
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return record
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="Concurrent allocation conflict: slot taken")
"""
        workspace.write_file("app/services/allocation_service.py", service_code)

        # 6. Seed Items Code Generation
        seed_lines = []
        for s in spec.seed_items:
            seed_lines.append(f'            {item_cls}(name="{s["name"]}", {spec.item_attr1_name}="{s["attr1"]}", {spec.item_attr2_name}="{s["attr2"]}"),')
        seeds_str = "\n".join(seed_lines)
        options_repr = repr(spec.seed_options)

        # 7. app/main.py
        workspace.write_file("app/main.py", f"""import hashlib
import json
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.models import User, {item_cls}, {alloc_cls}, AuditLog
from app.services.allocation_service import execute_allocation

# Initialize tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="{spec.project_name}",
    version="1.0.0",
    description="Engineered by ForgeSwarm Autonomous Engineering Swarm"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seed initial {spec.item_plural} if empty
def seed_catalog():
    db = next(get_db())
    if db.query({item_cls}).count() == 0:
        items = [
{seeds_str}
        ]
        db.add_all(items)
        db.commit()
    db.close()

seed_catalog()

# Schemas
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class AllocationRequest(BaseModel):
    {spec.item_singular}_id: int
    slot_time: str
    notes: Optional[str] = "Standard allocation request"

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication token required (SEC-001)")
    token = authorization.split(" ")[1]
    user = db.query(User).filter(User.email == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session token")
    return user

@app.get("/health")
def health():
    return {{"status": "HEALTHY", "system": "{spec.project_name}", "domain": "{spec.domain}", "version": "1.0.0"}}

@app.post("/api/auth/register", status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Account with this email already exists")
    user = User(name=req.name, email=req.email, password_hash=hash_pw(req.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {{"token": user.email, "user": {{"id": user.id, "name": user.name, "email": user.email}}}}

@app.post("/api/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email, User.password_hash == hash_pw(req.password)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {{"token": user.email, "user": {{"id": user.id, "name": user.name, "email": user.email}}}}

@app.get("/api/{spec.item_plural}")
def list_{spec.item_plural}(db: Session = Depends(get_db)):
    items = db.query({item_cls}).all()
    return [
        {{"id": i.id, "name": i.name, "{spec.item_attr1_name}": getattr(i, "{spec.item_attr1_name}"), "{spec.item_attr2_name}": getattr(i, "{spec.item_attr2_name}")}}
        for i in items
    ]

# Backward compatibility alias
@app.get("/api/doctors")
def list_doctors_alias(db: Session = Depends(get_db)):
    return list_{spec.item_plural}(db)

@app.get("/api/{spec.item_plural}/{{{spec.item_singular}_id}}/slots")
def get_{spec.item_singular}_slots({spec.item_singular}_id: int, date: str = "2026-10-15", db: Session = Depends(get_db)):
    item = db.query({item_cls}).filter({item_cls}.id == {spec.item_singular}_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="{item_cls} not found")
    all_slots = {options_repr}
    
    allocated = db.query({alloc_cls}.slot_time).filter(
        {alloc_cls}.{spec.item_singular}_id == {spec.item_singular}_id,
        {alloc_cls}.status == "ACTIVE"
    ).all()
    allocated_times = {{a[0] for a in allocated}}
    
    return [
        {{"slot": slot, "available": slot not in allocated_times}}
        for slot in all_slots
    ]

@app.post("/api/allocations", status_code=201)
def create_allocation(req: AllocationRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query({item_cls}).filter({item_cls}.id == req.{spec.item_singular}_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="{item_cls} not found")
    rec = execute_allocation(db, req.{spec.item_singular}_id, user.id, req.slot_time, req.notes)
    return {{
        "id": rec.id,
        "{spec.item_singular}_id": rec.{spec.item_singular}_id,
        "item_name": item.name,
        "slot_time": rec.slot_time,
        "notes": rec.notes,
        "status": rec.status
    }}

# Backward-compat alias for appointments endpoint
@app.post("/api/appointments", status_code=201)
def create_appointment_alias(req: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    target_id = req.get("{spec.item_singular}_id") or req.get("doctor_id") or 1
    slot = req.get("slot_time") or req.get("appointment_time") or "2026-10-15 Slot 1 (09:00 AM)"
    notes = req.get("notes") or req.get("reason") or "Standard request"
    alloc_req = AllocationRequest({spec.item_singular}_id=target_id, slot_time=slot, notes=notes)
    return create_allocation(alloc_req, user, db)

@app.get("/api/allocations")
def list_allocations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query({alloc_cls}).filter({alloc_cls}.user_id == user.id).all()
    result = []
    for r in records:
        result.append({{
            "id": r.id,
            "{spec.item_singular}_id": r.{spec.item_singular}_id,
            "item_name": r.{spec.item_singular}.name if r.{spec.item_singular} else "Item",
            "slot_time": r.slot_time,
            "notes": r.notes,
            "status": r.status
        }})
    return result

@app.get("/api/appointments")
def list_appointments_alias(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list_allocations(user, db)

@app.delete("/api/allocations/{{allocation_id}}")
def cancel_allocation(allocation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = db.query({alloc_cls}).filter(
        {alloc_cls}.id == allocation_id,
        {alloc_cls}.user_id == user.id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Allocation not found or not owned by user")
    record.status = "CANCELLED"
    db.commit()
    return {{"message": "Allocation successfully released", "status": "CANCELLED"}}

@app.delete("/api/appointments/{{appointment_id}}")
def cancel_appointment_alias(appointment_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return cancel_allocation(appointment_id, user, db)

@app.get("/api/audit-logs")
def get_audit_logs(db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(20).all()
    return [{{"id": l.id, "action": l.action, "entity_name": l.entity_name, "entity_id": l.entity_id, "details": l.details, "timestamp": str(l.timestamp)}} for l in logs]

@app.get("/", response_class=HTMLResponse)
def index_page():
    return \"\"\"<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{spec.project_name} — Generated by ForgeSwarm</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body {{ background: #0B1120; color: #F8FAFC; font-family: system-ui, sans-serif; }}
  </style>
</head>
<body class="p-6 max-w-5xl mx-auto">
  <header class="border-b border-slate-700 pb-4 mb-6 flex justify-between items-center">
    <div>
      <div class="flex items-center space-x-2">
        <span class="w-3 h-3 rounded-full bg-cyan-400 animate-pulse"></span>
        <h1 class="text-2xl font-bold text-white tracking-tight">{spec.project_name}</h1>
      </div>
      <p class="text-sm text-slate-400 mt-1">Domain: <span class="text-cyan-400 font-semibold">{spec.domain}</span> | Engineered by <span class="text-cyan-300 font-semibold">ForgeSwarm</span></p>
    </div>
    <div id="auth-status" class="text-right text-xs text-slate-400">Not authenticated</div>
  </header>

  <div id="app-container" class="grid grid-cols-1 md:grid-cols-3 gap-6">
    <!-- Auth Card -->
    <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <h2 class="text-lg font-semibold text-cyan-400 mb-3" id="auth-title">User Authentication</h2>
      <div id="auth-form" class="space-y-2">
        <input id="name-input" type="text" placeholder="Full Name" class="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm text-white" value="Jordan Hayes">
        <input id="email-input" type="email" placeholder="Email Address" class="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm text-white" value="jordan@example.com">
        <input id="pass-input" type="password" placeholder="Password" class="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm text-white" value="Secret123!">
        <div class="flex space-x-2 pt-1">
          <button onclick="handleRegister()" class="flex-1 bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold py-2 px-3 rounded transition">Register</button>
          <button onclick="handleLogin()" class="flex-1 bg-slate-800 hover:bg-slate-700 border border-slate-600 text-white text-xs font-semibold py-2 px-3 rounded transition">Sign In</button>
        </div>
      </div>
      <div id="user-info" class="hidden">
        <p class="text-sm text-slate-300">Signed in as: <strong id="logged-user" class="text-emerald-400">Jordan</strong></p>
        <button onclick="handleLogout()" class="mt-3 text-xs bg-rose-900/60 hover:bg-rose-800 text-rose-200 px-3 py-1.5 rounded">Sign Out</button>
      </div>
      <div id="auth-alert" class="mt-3 text-xs p-2 rounded hidden"></div>
    </div>

    <!-- Catalog & Selection Panel -->
    <div class="md:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <h2 class="text-lg font-semibold text-cyan-400 mb-3">{spec.catalog_title}</h2>
      <div id="item-list" class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
        <div class="text-xs text-slate-500">Loading catalog...</div>
      </div>

      <div id="slot-container" class="mt-4 pt-4 border-t border-slate-800 hidden">
        <h3 class="text-sm font-semibold text-slate-200 mb-3">{spec.action_label} for <span id="selected-item-name" class="text-cyan-300"></span></h3>
        <div class="mb-3">
          <label class="block text-xs font-mono uppercase text-slate-400 mb-1.5">{spec.options_label}:</label>
          <div id="slot-buttons" class="grid grid-cols-1 sm:grid-cols-2 gap-2"></div>
        </div>
        <div class="space-y-2">
          <label class="block text-xs font-mono uppercase text-slate-400">{spec.primary_input_label}:</label>
          <input id="notes-input" type="text" placeholder="{spec.primary_input_placeholder}" class="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500">
          <button onclick="bookSelectedSlot()" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold py-2.5 px-4 rounded-lg transition mt-2">{spec.action_label}</button>
        </div>
        <div id="booking-alert" class="mt-3 text-xs p-2 rounded hidden"></div>
      </div>
    </div>
  </div>

  <!-- User Records History -->
  <div class="mt-6 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
    <div class="flex justify-between items-center mb-3">
      <h2 class="text-lg font-semibold text-cyan-400">{spec.record_title} (FR-006 Traceability)</h2>
      <button onclick="fetchAllocations()" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1 rounded">Refresh</button>
    </div>
    <div id="allocations-list" class="divide-y divide-slate-800 text-sm">
      <div class="text-xs text-slate-500 py-2">No active records or not signed in.</div>
    </div>
  </div>

  <script>
    let currentToken = null;
    let selectedItemId = null;
    let selectedSlot = null;

    async function handleRegister() {{
      const name = document.getElementById('name-input').value;
      const email = document.getElementById('email-input').value;
      const password = document.getElementById('pass-input').value;
      try {{
        const res = await fetch('/api/auth/register', {{
          method: 'POST',
          headers: {{'Content-Type': 'application/json'}},
          body: JSON.stringify({{name, email, password}})
        }});
        const data = await res.json();
        if (res.ok) {{
          currentToken = data.token;
          onAuthSuccess(data.user.name);
          showAlert('auth-alert', 'Registered successfully!', 'emerald');
        }} else {{
          showAlert('auth-alert', data.detail || 'Registration failed', 'rose');
        }}
      }} catch (err) {{
        showAlert('auth-alert', 'Network error', 'rose');
      }}
    }}

    async function handleLogin() {{
      const email = document.getElementById('email-input').value;
      const password = document.getElementById('pass-input').value;
      try {{
        const res = await fetch('/api/auth/login', {{
          method: 'POST',
          headers: {{'Content-Type': 'application/json'}},
          body: JSON.stringify({{email, password}})
        }});
        const data = await res.json();
        if (res.ok) {{
          currentToken = data.token;
          onAuthSuccess(data.user.name);
          showAlert('auth-alert', 'Signed in successfully!', 'emerald');
        }} else {{
          showAlert('auth-alert', data.detail || 'Login failed', 'rose');
        }}
      }} catch (err) {{
        showAlert('auth-alert', 'Network error', 'rose');
      }}
    }}

    function onAuthSuccess(userName) {{
      document.getElementById('auth-form').classList.add('hidden');
      document.getElementById('user-info').classList.remove('hidden');
      document.getElementById('logged-user').innerText = userName;
      document.getElementById('auth-status').innerText = 'Authenticated (' + userName + ')';
      fetchAllocations();
    }}

    function handleLogout() {{
      currentToken = null;
      document.getElementById('auth-form').classList.remove('hidden');
      document.getElementById('user-info').classList.add('hidden');
      document.getElementById('auth-status').innerText = 'Not authenticated';
      document.getElementById('allocations-list').innerHTML = '<div class="text-xs text-slate-500 py-2">Signed out.</div>';
    }}

    function showAlert(elemId, msg, color) {{
      const el = document.getElementById(elemId);
      el.className = `mt-3 text-xs p-2 rounded bg-${{color}}-900/50 text-${{color}}-200 border border-${{color}}-700 block`;
      el.innerText = msg;
    }}

    async function fetchItems() {{
      const res = await fetch('/api/{spec.item_plural}');
      const items = await res.json();
      const container = document.getElementById('item-list');
      container.innerHTML = items.map(i => `
        <div onclick="selectItem(${{i.id}}, '${{i.name}}')" class="p-3.5 bg-slate-800/80 hover:bg-slate-700/80 cursor-pointer rounded-lg border border-slate-700 transition flex flex-col justify-between">
          <div>
            <div class="font-semibold text-white text-sm">${{i.name}}</div>
            <div class="text-xs text-cyan-400 mt-1 font-medium">${{i.{spec.item_attr1_name}}}</div>
            <div class="text-xs text-slate-400 mt-0.5">${{i.{spec.item_attr2_name}}}</div>
          </div>
          <button class="mt-3 text-[11px] bg-cyan-950/80 hover:bg-cyan-900 border border-cyan-700 text-cyan-300 font-semibold px-2.5 py-1 rounded w-fit">{spec.action_label}</button>
        </div>
      `).join('');
    }}

    async function selectItem(id, name) {{
      selectedItemId = id;
      document.getElementById('selected-item-name').innerText = name;
      document.getElementById('slot-container').classList.remove('hidden');
      
      const res = await fetch(`/api/{spec.item_plural}/${{id}}/slots`);
      const slots = await res.json();
      const container = document.getElementById('slot-buttons');
      container.innerHTML = slots.map(s => `
        <button onclick="chooseSlot('${{s.slot}}')" class="text-xs p-2 rounded border text-center transition ${{
          s.available ? 'bg-slate-800 hover:bg-cyan-900 border-slate-700 text-slate-200' : 'bg-slate-900 text-slate-600 border-slate-800 cursor-not-allowed opacity-50'
        }}" ${{!s.available ? 'disabled' : ''}}>
          ${{s.slot}}
        </button>
      `).join('');
    }}

    function chooseSlot(slot) {{
      selectedSlot = slot;
      showAlert('booking-alert', 'Selected: ' + slot, 'cyan');
    }}

    async function bookSelectedSlot() {{
      if (!currentToken) {{
        alert('Please register or sign in first!');
        return;
      }}
      if (!selectedItemId || !selectedSlot) {{
        alert('Please select an item and option first!');
        return;
      }}
      const notes = document.getElementById('notes-input').value;
      try {{
        const res = await fetch('/api/allocations', {{
          method: 'POST',
          headers: {{
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + currentToken
          }},
          body: JSON.stringify({{
            {spec.item_singular}_id: selectedItemId,
            slot_time: selectedSlot,
            notes: notes
          }})
        }});
        const data = await res.json();
        if (res.ok) {{
          showAlert('booking-alert', 'Successfully processed ' + data.item_name + ' (' + data.slot_time + ')', 'emerald');
          fetchAllocations();
          selectItem(selectedItemId, document.getElementById('selected-item-name').innerText);
        }} else {{
          showAlert('booking-alert', 'Conflict / Error: ' + (data.detail || 'Request Conflict'), 'rose');
        }}
      }} catch (err) {{
        showAlert('booking-alert', 'Network error during request', 'rose');
      }}
    }}

    async function fetchAllocations() {{
      if (!currentToken) return;
      const res = await fetch('/api/allocations', {{
        headers: {{'Authorization': 'Bearer ' + currentToken}}
      }});
      const data = await res.json();
      const container = document.getElementById('allocations-list');
      if (data.length === 0) {{
        container.innerHTML = '<div class="text-xs text-slate-500 py-2">No active records.</div>';
        return;
      }}
      container.innerHTML = data.map(a => `
        <div class="py-3 flex justify-between items-center">
          <div>
            <div class="font-semibold text-white text-sm">${{a.item_name}}</div>
            <div class="text-xs text-cyan-300 font-mono mt-0.5">${{a.slot_time}}</div>
            ${{a.notes ? `<div class="text-xs text-slate-300 mt-1 italic">${{a.notes}}</div>` : ''}}
            <div class="mt-1.5">
              <span class="text-[10px] font-mono uppercase px-2 py-0.5 rounded ${{a.status === 'ACTIVE' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-slate-800 text-slate-400'}}">${{a.status === 'ACTIVE' ? 'SUBMITTED (VERIFIED)' : a.status}}</span>
            </div>
          </div>
          ${{a.status === 'ACTIVE' ? `<button onclick="cancelAlloc(${{a.id}})" class="text-xs bg-rose-950/70 hover:bg-rose-900 border border-rose-800 text-rose-300 px-3 py-1.5 rounded transition font-medium">{spec.action_reverse.capitalize()}</button>` : ''}}
        </div>
      `).join('');
    }}

    async function cancelAlloc(id) {{
      const res = await fetch(`/api/allocations/${{id}}`, {{
        method: 'DELETE',
        headers: {{'Authorization': 'Bearer ' + currentToken}}
      }});
      if (res.ok) {{
        fetchAllocations();
        if (selectedItemId) {{
          selectItem(selectedItemId, document.getElementById('selected-item-name').innerText);
        }}
      }}
    }}

    fetchItems();
  </script>
</body>
</html>\"\"\"
""")

        # 8. tests/test_suite.py (17 Requirement-Based Tests mapped to user domain)
        workspace.write_file("tests/test_suite.py", f"""import pytest
import concurrent.futures
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield

# --- FR-001: User Registration & Auth ---
def test_fr_001_user_registration_success():
    resp = client.post("/api/auth/register", json={{
        "name": "Alex Vance",
        "email": "alex.vance@swarm-test.org",
        "password": "SecurePassword123!"
    }})
    assert resp.status_code == 201
    data = resp.json()
    assert "token" in data
    assert data["user"]["email"] == "alex.vance@swarm-test.org"

def test_fr_001_duplicate_registration_rejection():
    resp = client.post("/api/auth/register", json={{
        "name": "Duplicate User",
        "email": "alex.vance@swarm-test.org",
        "password": "AnotherPassword!"
    }})
    assert resp.status_code == 400

def test_fr_001_login_valid_credentials():
    resp = client.post("/api/auth/login", json={{
        "email": "alex.vance@swarm-test.org",
        "password": "SecurePassword123!"
    }})
    assert resp.status_code == 200
    assert "token" in resp.json()

def test_fr_001_login_invalid_password():
    resp = client.post("/api/auth/login", json={{
        "email": "alex.vance@swarm-test.org",
        "password": "WrongPassword!"
    }})
    assert resp.status_code == 401

# --- FR-002: Catalog Listing ---
def test_fr_002_list_items():
    resp = client.get("/api/{spec.item_plural}")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 4

# --- FR-003: Slot Availability Inspection ---
def test_fr_003_available_slots_retrieval():
    resp = client.get("/api/{spec.item_plural}/1/slots")
    assert resp.status_code == 200
    slots = resp.json()
    assert len(slots) > 0
    assert any(s["available"] is True for s in slots)

# --- SEC-001: Unauthenticated Allocation Blocked ---
def test_sec_001_unauthenticated_allocation_blocked():
    resp = client.post("/api/allocations", json={{
        "{spec.item_singular}_id": 1,
        "slot_time": "2026-10-15 Slot 1 (09:00 AM)",
        "notes": "Test"
    }})
    assert resp.status_code == 401

# --- FR-004: Authenticated Allocation Success ---
def test_fr_004_authenticated_allocation_success():
    resp = client.post("/api/allocations", 
        headers={{"Authorization": "Bearer alex.vance@swarm-test.org"}},
        json={{
            "{spec.item_singular}_id": 1,
            "slot_time": "2026-10-15 Slot 1 (09:00 AM)",
            "notes": "Priority Reservation"
        }}
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "ACTIVE"

def test_fr_003_slot_status_updated_after_allocation():
    resp = client.get("/api/{spec.item_plural}/1/slots")
    slots = resp.json()
    booked = next(s for s in slots if s["slot"] == "2026-10-15 Slot 1 (09:00 AM)")
    assert booked["available"] is False

# --- FR-005: Release / Cancellation Workflow ---
def test_fr_005_cancellation_workflow():
    alloc_resp = client.post("/api/allocations", 
        headers={{"Authorization": "Bearer alex.vance@swarm-test.org"}},
        json={{
            "{spec.item_singular}_id": 2,
            "slot_time": "2026-10-15 Slot 4 (01:00 PM)",
            "notes": "Temporary"
        }}
    )
    alloc_id = alloc_resp.json()["id"]
    
    cancel_resp = client.delete(f"/api/allocations/{{alloc_id}}",
        headers={{"Authorization": "Bearer alex.vance@swarm-test.org"}}
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "CANCELLED"

def test_fr_005_slot_reopened_after_cancellation():
    resp = client.get("/api/{spec.item_plural}/2/slots")
    slots = resp.json()
    reopened = next(s for s in slots if s["slot"] == "2026-10-15 Slot 4 (01:00 PM)")
    assert reopened["available"] is True

# --- FR-006: User Allocation History ---
def test_fr_006_user_allocation_history():
    resp = client.get("/api/allocations",
        headers={{"Authorization": "Bearer alex.vance@swarm-test.org"}}
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

# --- SEC-002: Password Hashing Verification ---
def test_sec_002_password_not_stored_plaintext():
    from app.models import User
    from app.database import SessionLocal
    db = SessionLocal()
    user = db.query(User).filter(User.email == "alex.vance@swarm-test.org").first()
    assert user.password_hash != "SecurePassword123!"
    assert len(user.password_hash) == 64
    db.close()

# --- Boundary & Reliability Tests ---
def test_fr_004_nonexistent_item_rejection():
    resp = client.post("/api/allocations", 
        headers={{"Authorization": "Bearer alex.vance@swarm-test.org"}},
        json={{
            "{spec.item_singular}_id": 99999,
            "slot_time": "2026-10-15 Slot 1 (09:00 AM)"
        }}
    )
    assert resp.status_code == 404

def test_fr_005_cancel_unauthorized_allocation_fails():
    resp = client.delete("/api/allocations/99999",
        headers={{"Authorization": "Bearer alex.vance@swarm-test.org"}}
    )
    assert resp.status_code == 404

def test_health_check_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "HEALTHY"

# --- BR-001: CONCURRENCY INVARIANT PROBE ---
def test_br_001_concurrency_invariant_prevention():
    \"\"\"
    CRITICAL ACCEPTANCE TEST ({spec.concurrency_invariant_title}):
    Given two users attempt to allocate the exact same {spec.item_singular} and slot simultaneously:
    EXPECTED: Exactly ONE succeeds (HTTP 201), the second MUST FAIL safely (HTTP 409 Conflict).
    \"\"\"
    client.post("/api/auth/register", json={{"name": "User Alpha", "email": "alpha.concurrency@test.com", "password": "pass"}})
    client.post("/api/auth/register", json={{"name": "User Beta", "email": "beta.concurrency@test.com", "password": "pass"}})

    target_slot = "2026-10-15 Slot 2 (10:00 AM)"
    target_item_id = 1

    results = []

    def make_allocation(email):
        local_client = TestClient(app)
        res = local_client.post("/api/allocations",
            headers={{"Authorization": f"Bearer {{email}}"}},
            json={{
                "{spec.item_singular}_id": target_item_id,
                "slot_time": target_slot,
                "notes": f"Concurrent allocation probe from {{email}}"
            }}
        )
        return res.status_code

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(make_allocation, "alpha.concurrency@test.com")
        f2 = executor.submit(make_allocation, "beta.concurrency@test.com")
        results = [f1.result(), f2.result()]

    successes = results.count(201)
    conflicts = results.count(409)

    # In the defective version, BOTH requests will return 201 (successes == 2), which fails this assertion!
    # In the repaired version, exactly one is 201 and the other is 409.
    assert successes == 1, f"BR-001 VIOLATION: Expected 1 booking success, got {{successes}}. Status codes: {{results}}"
    assert conflicts == 1, f"Expected 1 conflict rejection (409), got {{conflicts}}."
""")

        return workspace.list_files()
