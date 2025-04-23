# --- Imports for both CLI and API ---
import json
import os
import uuid
import datetime
import enum
import secrets
import argparse
import sys
from typing import List, Optional
from decimal import Decimal, InvalidOperation # Used by both, but Decimal handling differs slightly

# --- Imports specific to CLI ---
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress_bar import ProgressBar
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
    import locale
    RICH_AVAILABLE = True
except ImportError:
    print("Rich library not found. CLI mode will be unavailable.")
    RICH_AVAILABLE = False
    # Mock Rich components for minimal errors if CLI mode is attempted
    class MockConsole:
        def print(self, *args, **kwargs): pass
        def rule(self, *args, **kwargs): pass
    class MockTable:
        def __init__(self, *args, **kwargs): pass
        def add_column(self, *args, **kwargs): pass
        def add_row(self, *args, **kwargs): pass
    class MockPanel:
         def __init__(self, *args, **kwargs): pass
    class MockProgressBar:
         def __init__(self, *args, **kwargs): pass
         def __rich_console__(self, console, options): return "" # Make it render empty
    class MockPrompt:
        def ask(self, *args, **kwargs): return input(args[0] + " ")
    class MockConfirm:
        def ask(self, *args, **kwargs): return input(args[0] + " (y/n): ").lower().startswith('y')
    class MockText:
        @staticmethod
        def assemble(*args): return "".join(str(a) for a in args)

    Console = MockConsole
    Table = MockTable
    Panel = MockPanel
    ProgressBar = MockProgressBar
    Prompt = MockPrompt
    Confirm = MockConfirm
    Text = MockText
    locale = None # Ensure locale is None if rich isn't available

# --- Imports specific to API ---
try:
    from fastapi import FastAPI, Depends, HTTPException, status, Query, Security
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.security.api_key import APIKeyHeader
    from sqlalchemy import (
        create_engine, Column, Integer, String, Float, DateTime, Boolean, Enum as SQLAlchemyEnum,
        ForeignKey, desc, asc
    )
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, Session, relationship
    from pydantic import BaseModel, Field
    from passlib.context import CryptContext
    from dotenv import load_dotenv
    import uvicorn
    import re # Used for username validation
    FASTAPI_AVAILABLE = True
except ImportError:
    print("FastAPI, SQLAlchemy, Pydantic, Passlib, or Uvicorn not found. API mode and --create-user will be unavailable.")
    FASTAPI_AVAILABLE = False
    # Mock FastAPI components minimally if needed to avoid parse errors
    class MockFastAPI:
        def get(self, *args, **kwargs): return lambda func: func
        def post(self, *args, **kwargs): return lambda func: func
        def put(self, *args, **kwargs): return lambda func: func
        def delete(self, *args, **kwargs): return lambda func: func
        def add_middleware(self, *args, **kwargs): pass
    FastAPI = MockFastAPI
    Depends = None
    HTTPException = Exception # Simple Exception mock
    status = type('MockStatus', (object,), {'HTTP_400_BAD_REQUEST': 400, 'HTTP_404_NOT_FOUND': 404, 'HTTP_401_UNAUTHORIZED': 401, 'HTTP_201_CREATED': 201, 'HTTP_204_NO_CONTENT': 204})
    Query = lambda *args, **kwargs: None
    Security = lambda *args, **kwargs: None
    APIKeyHeader = lambda *args, **kwargs: None
    create_engine = None
    Column = None
    Integer = None
    String = None
    Float = None
    DateTime = None
    Boolean = None
    SQLAlchemyEnum = lambda x: None
    ForeignKey = None
    desc = lambda x: x
    asc = lambda x: x
    declarative_base = lambda: type('MockBase', (object,), {'metadata': type('MockMetadata', (object,), {'create_all': lambda self, bind: None})})()
    sessionmaker = lambda *args, **kwargs: None
    Session = None
    relationship = None
    BaseModel = object
    Field = lambda *args, **kwargs: None
    CryptContext = lambda *args, **kwargs: type('MockCryptContext', (object,), {'hash': lambda self, x: x, 'verify': lambda self, x, y: x == y})()
    load_dotenv = lambda: None
    uvicorn = None
    re = None


# --- API Configuration & Environment Loading ---
if FASTAPI_AVAILABLE:
    load_dotenv() # Load environment variables from .env file

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./db.sqlite")
    BACKEND_SECRET_KEY = os.getenv("BACKEND_SECRET_KEY", "default_secret_key_change_me") # Fallback, but .env is preferred

    # --- Database Setup ---
    is_sqlite = DATABASE_URL.startswith("sqlite")
    engine_args = {"check_same_thread": False} if is_sqlite else {}
    try:
         engine = create_engine(DATABASE_URL, connect_args=engine_args)
         SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
         Base = declarative_base()
         DB_SETUP_SUCCESS = True
    except Exception as e:
        print(f"Failed to connect to database or setup SQLAlchemy: {e}", file=sys.stderr)
        print("API mode will not be functional.", file=sys.stderr)
        engine = None
        SessionLocal = None
        Base = type('MockBase', (object,), {'metadata': type('MockMetadata', (object,), {'create_all': lambda self, bind: None})})()
        DB_SETUP_SUCCESS = False


# --- Enums (Used by both, define once) ---
class GoalPriority(str, enum.Enum):
    high = "high"
    medium = "medium"
    low = "low"

# --- Database Models (SQLAlchemy ORM - API Only) ---
if FASTAPI_AVAILABLE and DB_SETUP_SUCCESS:
    class User(Base):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True, index=True)
        username = Column(String, unique=True, index=True, nullable=False)
        hashed_api_key = Column(String, unique=True, nullable=False) # Store HASH only
        is_active = Column(Boolean, default=True)
        created_at = Column(DateTime, default=datetime.datetime.utcnow)
        goals = relationship("Goal", back_populates="owner", cascade="all, delete-orphan")

    class Goal(Base):
        __tablename__ = "goals"
        id = Column(Integer, primary_key=True, index=True)
        name = Column(String, index=True, nullable=False)
        target = Column(Float, nullable=False)
        current = Column(Float, default=0.0, nullable=False)
        priority = Column(SQLAlchemyEnum(GoalPriority), default=GoalPriority.medium, nullable=False)
        added_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
        last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
        owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
        owner = relationship("User", back_populates="goals")
        # Example constraint: UniqueConstraint('owner_id', 'name', name='uq_user_goal_name')
else:
     # Mock models if DB setup fails
     class User: pass
     class Goal: pass


# --- Pydantic Schemas (Data Validation & Serialization - API Only) ---
if FASTAPI_AVAILABLE:
    class GoalBase(BaseModel):
        name: str = Field(..., max_length=100)
        target: float = Field(..., gt=0)
        priority: GoalPriority = GoalPriority.medium

    class GoalCreate(GoalBase):
        pass

    class GoalUpdate(BaseModel):
        name: Optional[str] = Field(None, max_length=100)
        target: Optional[float] = Field(None, gt=0)
        priority: Optional[GoalPriority] = None

    class GoalContribution(BaseModel):
        amount: float = Field(..., gt=0)

    class GoalResponse(GoalBase): # Renamed from 'Goal' to avoid conflict with model
        id: int
        current: float = 0.0
        added_date: datetime.datetime
        last_updated: datetime.datetime
        owner_id: int
        class Config:
            orm_mode = True

    class UserBase(BaseModel):
        username: str = Field(..., min_length=3, max_length=50, regex="^[A-Z0-9_-]+$")

    class UserCreate(UserBase):
        pass

    class UserResponse(UserBase): # Renamed from 'User' to avoid conflict with model
        id: int
        is_active: bool
        created_at: datetime.datetime
        class Config:
            orm_mode = True

# --- Authentication & Security (API Only) ---
if FASTAPI_AVAILABLE:
    API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=True)
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    # --- Database Dependency ---
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    # --- CRUD Operations (Create, Read, Update, Delete - API Only) ---

    # User CRUD
    def crud_get_user(db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    def crud_get_user_by_username(db: Session, username: str):
        return db.query(User).filter(User.username == username.upper()).first()

    def crud_get_all_users(db: Session, skip: int = 0, limit: int = 100): # Inefficient for many users!
        return db.query(User).offset(skip).limit(limit).all()

    def crud_create_user(db: Session, username: str, plain_api_key: str):
        hashed_key = get_password_hash(plain_api_key)
        db_user = User(username=username.upper(), hashed_api_key=hashed_key)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    # Goal CRUD
    def crud_get_goal(db: Session, goal_id: int, owner_id: int):
        return db.query(Goal).filter(Goal.id == goal_id, Goal.owner_id == owner_id).first()

    def crud_get_goals_by_user(
        db: Session, owner_id: int, sort_by: str = "date", sort_dir: str = "desc", skip: int = 0, limit: int = 100
    ):
        query = db.query(Goal).filter(Goal.owner_id == owner_id)
        # Using the database's sorting capabilities where possible
        direction_func = desc if sort_dir == "desc" else asc

        if sort_by == "name":
            query = query.order_by(direction_func(Goal.name))
        elif sort_by == "target":
            query = query.order_by(direction_func(Goal.target))
        elif sort_by == "priority":
            # Order by priority value
            priority_order = {GoalPriority.high: 3, GoalPriority.medium: 2, GoalPriority.low: 1}
            priority_clause = case(priority_order, value=Goal.priority)
            query = query.order_by(direction_func(priority_clause))
        elif sort_by == "remaining":
            # Calculate remaining in the query or sort after fetching
            # Sorting after fetching is simpler here to reuse crud_get_goals_by_user structure
            all_goals = query.all()
            all_goals.sort(key=lambda g: max(0, g.target - g.current), reverse=(sort_dir == "desc"))
            return all_goals[skip : skip + limit]
        elif sort_by == "progress":
            # Calculate progress after fetching
            all_goals = query.all()
            all_goals.sort(key=lambda g: (g.current / g.target * 100) if g.target > 0 else 0, reverse=(sort_dir == "desc"))
            return all_goals[skip : skip + limit]
        elif sort_by == "date":
             query = query.order_by(direction_func(Goal.added_date)) # Default
        else: # Fallback to date sort if sort_by is invalid (should be caught by validation though)
             query = query.order_by(direction_func(Goal.added_date))


        return query.offset(skip).limit(limit).all()

    # Need case statement for priority sorting in SQLAlchemy
    from sqlalchemy import case

    def crud_create_goal(db: Session, goal: GoalCreate, owner_id: int):
        existing_goal = db.query(Goal).filter(Goal.owner_id == owner_id, Goal.name.ilike(goal.name)).first() # Case-insensitive check
        if existing_goal: return None
        db_goal = Goal(**goal.dict(), owner_id=owner_id, current=0.0, added_date=datetime.datetime.utcnow(), last_updated=datetime.datetime.utcnow())
        db.add(db_goal)
        db.commit()
        db.refresh(db_goal)
        return db_goal

    def crud_add_contribution(db: Session, goal_id: int, owner_id: int, amount: float):
        db_goal = crud_get_goal(db=db, goal_id=goal_id, owner_id=owner_id)
        if db_goal:
            db_goal.current += amount
            db_goal.last_updated = datetime.datetime.utcnow()
            db.commit()
            db.refresh(db_goal)
            return db_goal
        return None

    def crud_update_goal(db: Session, goal_id: int, owner_id: int, goal_update: GoalUpdate):
        db_goal = crud_get_goal(db=db, goal_id=goal_id, owner_id=owner_id)
        if not db_goal: return None
        update_data = goal_update.dict(exclude_unset=True)
        if "name" in update_data and update_data["name"].lower() != db_goal.name.lower(): # Case-insensitive check
             existing = db.query(Goal).filter(Goal.owner_id == owner_id, Goal.name.ilike(update_data["name"]), Goal.id != goal_id).first()
             if existing: return "DUPLICATE_NAME" # Use a specific return value to signal this
        for key, value in update_data.items():
            setattr(db_goal, key, value)
        db_goal.last_updated = datetime.datetime.utcnow()
        db.commit()
        db.refresh(db_goal)
        return db_goal


    def crud_delete_goal(db: Session, goal_id: int, owner_id: int):
        db_goal = crud_get_goal(db=db, goal_id=goal_id, owner_id=owner_id)
        if db_goal:
            db.delete(db_goal)
            db.commit()
            return True
        return False

    # --- Authentication Dependency ---
    async def get_current_user(
        api_key_header: str = Security(API_KEY_HEADER),
        db: Session = Depends(get_db)
    ) -> User:
        """Dependency to authenticate user based on API Key hash lookup."""
        # This is inefficient for many users. A better approach would be to hash
        # the incoming key, salt it with a known constant (or derived from a secret),
        # and compare directly to stored hashes, IF the hashing function allows.
        # bcrypt doesn't allow this directly. A better production design might use
        # salted, hashed API keys stored alongside a lookup key (not the full key),
        # or JWTs issued after initial API key validation.
        # For this demo, iterating and verifying is acceptable.
        authenticated_user = None
        # Optimize lookup slightly if possible (e.g., if keys had a structure allowing partial lookup)
        # Simple linear scan for now:
        users = db.query(User).filter(User.is_active == True).all() # Only check active users
        for user in users:
            if verify_password(api_key_header, user.hashed_api_key):
                 authenticated_user = user
                 break

        if authenticated_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API Key", # Removed "or inactive user" as we filter inactive in query
                headers={"WWW-Authenticate": "API Key"},
            )
        return authenticated_user

    # --- FastAPI Application Setup ---
    app = FastAPI(
        title="Savings Goal Tracker API",
        description="API backend for the IBM 5153 Savings Goal Tracker (Single File)",
        version="1.1.0",
        # Disable interactive docs if DB setup failed, or enable based on flag
        docs_url="/docs" if DB_SETUP_SUCCESS else None,
        redoc_url="/redoc" if DB_SETUP_SUCCESS else None
    )

    # CORS Middleware
    origins = ["http://localhost", "http://localhost:8080", "http://127.0.0.1", "http://127.0.0.1:8080", "null"] # 'null' is often needed for local file testing
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*", "X-API-Key"],
    )

    # --- API Endpoints ---
    @app.get("/")
    async def read_root():
        return {"message": "Savings Goal Tracker API [5153] - Status: OPERATIONAL"}

    if DB_SETUP_SUCCESS: # Only add endpoints if DB is set up
        @app.post("/goals/", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
        async def create_new_goal_endpoint(
            goal: GoalCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
        ):
            # The crud_create_goal already handles duplicate names
            db_goal = crud_create_goal(db=db, goal=goal, owner_id=current_user.id)
            if db_goal is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Goal with name '{goal.name}' already exists.")
            return db_goal

        @app.get("/goals/", response_model=List[GoalResponse])
        async def read_user_goals_endpoint(
            sort_by: Optional[str] = Query("date", description="Sort criteria (date, priority, name, target, remaining, progress)", enum=["date", "priority", "name", "target", "remaining", "progress"]),
            sort_dir: Optional[str] = Query("desc", description="Sort direction (asc, desc)", enum=["asc", "desc"]),
            skip: int = 0, limit: int = Query(100, gt=0, le=1000), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
        ):
            # Input validation for sort_by and sort_dir is now handled by Query enum=
            goals = crud_get_goals_by_user(db, owner_id=current_user.id, sort_by=sort_by, sort_dir=sort_dir, skip=skip, limit=limit)
            return goals

        @app.get("/goals/{goal_id}/", response_model=GoalResponse)
        async def read_single_goal_endpoint(
            goal_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
        ):
            db_goal = crud_get_goal(db, goal_id=goal_id, owner_id=current_user.id)
            if db_goal is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found or access denied")
            return db_goal

        @app.post("/goals/{goal_id}/contribute/", response_model=GoalResponse)
        async def add_funds_to_goal_endpoint(
            goal_id: int, contribution: GoalContribution, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
        ):
            db_goal = crud_add_contribution(db, goal_id=goal_id, owner_id=current_user.id, amount=contribution.amount)
            if db_goal is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found or access denied")
            return db_goal

        @app.put("/goals/{goal_id}/", response_model=GoalResponse)
        async def update_existing_goal_endpoint(
            goal_id: int, goal_update: GoalUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
        ):
            updated_goal = crud_update_goal(db, goal_id=goal_id, owner_id=current_user.id, goal_update=goal_update)
            if updated_goal == "DUPLICATE_NAME":
                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot update: Another goal named '{goal_update.name}' exists.")
            if updated_goal is None:
                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found or access denied")
            return updated_goal

        @app.delete("/goals/{goal_id}/", status_code=status.HTTP_204_NO_CONTENT)
        async def delete_existing_goal_endpoint(
            goal_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
        ):
            deleted = crud_delete_goal(db, goal_id=goal_id, owner_id=current_user.id)
            if not deleted:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found or access denied")
            return None

        @app.get("/users/me/", response_model=UserResponse)
        async def read_users_me_endpoint(current_user: User = Depends(get_current_user)):
            return current_user

    @app.get("/health")
    async def health_check_endpoint():
        # Basic health check - maybe check DB connection?
        if FASTAPI_AVAILABLE and DB_SETUP_SUCCESS:
            try:
                db = SessionLocal()
                db.execute("SELECT 1") # Simple query to check connection
                db.close()
                return {"status": "ok", "database": "connected"}
            except Exception as e:
                 return {"status": "error", "database": f"connection failed ({e})"}
        else:
            return {"status": "ok", "database": "skipped/failed_setup"}


# --- API Key / User Creation Utility Logic (Uses API DB logic) ---
if FASTAPI_AVAILABLE and DB_SETUP_SUCCESS:
    def generate_api_key(prefix="sk_", length=32):
        """Generates a secure random API key."""
        key = secrets.token_urlsafe(length)
        return f"{prefix}{key}"

    def add_user_and_key_logic(username: str):
        """Adds a new user to the database with a generated API key."""
        print(f"--- Adding User: {username.upper()} ---")
        print(f"Using database: {DATABASE_URL}")
        try:
            Base.metadata.create_all(bind=engine) # Ensure tables exist
            db = SessionLocal()
            try:
                existing_user = crud_get_user_by_username(db, username=username)
                if existing_user:
                    print(f"Error: User '{username.upper()}' already exists (ID: {existing_user.id}).")
                    return
                new_api_key = generate_api_key()
                print(f"\n>>> Generated API Key: [bold green]{new_api_key}[/bold green] <<<", style="bold")
                print("    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                print("[bold red]    STORE THIS KEY SECURELY![/bold red] It will not be shown again.")
                user = crud_create_user(db=db, username=username, plain_api_key=new_api_key)
                print(f"\nSuccessfully created user '[bold cyan]{user.username}[/bold cyan]' with ID [yellow]{user.id}[/yellow].")
                print("[dim]API key has been hashed and stored.[/dim]")
            except Exception as e:
                db.rollback()
                print(f"\n[bold red]An error occurred during user creation:[/bold red] {e}", file=sys.stderr)
                print("[yellow]Database rolled back.[/yellow]")
            finally:
                db.close()
                print("------------------------------------")
        except Exception as e:
            print(f"[bold red]An error occurred during database setup or access:[/bold red] {e}", file=sys.stderr)
            print("[yellow]User creation aborted.[/yellow]")


# --- CLI Specific Code ---
if RICH_AVAILABLE:
    # --- CLI Configuration ---
    CLI_DATA_FILE = 'savings_tracker_cli_data.json' # Use a different file name to avoid conflicts
    cli_console = Console()

    # --- CLI Global State ---
    all_user_data_cli = {}
    current_user_cli = None
    current_sort_criteria_cli = 'date_desc'

    # Set locale for currency formatting if needed (example for India)
    try:
        # Use a different name for the CLI's locale function
        locale.setlocale(locale.LC_ALL, 'en_IN.UTF-8') # Adjust as needed for your system
        def format_currency_cli(amount):
            try:
                # Ensure it's a Decimal for precision
                return locale.currency(Decimal(amount), grouping=True, symbol="₹")
            except (TypeError, ValueError, InvalidOperation):
                return "₹?.??" # Handle invalid inputs gracefully
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8') # Fallback
            print("[yellow]Warning:[/yellow] Indian locale not found, using US locale for currency.")
            def format_currency_cli(amount):
                try:
                   return f"₹{Decimal(amount):,.2f}" # Basic INR format
                except (TypeError, ValueError):
                   return "₹?.??"
        except locale.Error:
            cli_console.print("[yellow]Warning:[/yellow] Could not set locale. Currency formatting might be basic.")
            # Basic fallback if locale setting fails entirely
            def format_currency_cli(amount):
                 try:
                     return f"₹{Decimal(amount):,.2f}" # Basic INR format
                 except (TypeError, ValueError):
                     return "₹?.??"

    # --- CLI Utility Functions ---
    def generate_id_cli():
        """Generates a short unique ID for CLI goals."""
        return uuid.uuid4().hex[:9]

    def get_priority_style_cli(priority):
        """Returns rich style string based on priority for CLI."""
        priority = (priority or 'medium').lower()
        if priority == 'high':
            return "[bold red]"
        elif priority == 'medium':
            return "[bold yellow]"
        elif priority == 'low':
            return "[dim green]"
        return "[white]" # Default

    def get_priority_value_cli(priority):
        """Returns a numerical value for sorting priorities in CLI."""
        priority = (priority or 'medium').lower()
        return {'high': 3, 'medium': 2, 'low': 1}.get(priority, 0)

    # --- CLI Data Persistence ---
    def load_data_cli():
        """Loads data from the CLI JSON file."""
        global all_user_data_cli, current_user_cli, current_sort_criteria_cli
        if os.path.exists(CLI_DATA_FILE):
            try:
                with open(CLI_DATA_FILE, 'r') as f:
                    data = json.load(f)
                    all_user_data_cli = data.get('allUserData', {})
                    # Convert numeric strings back to Decimals for goals
                    for uname, udata in all_user_data_cli.items():
                        if 'goals' in udata:
                            for goal in udata['goals']:
                                try: goal['target'] = Decimal(str(goal.get('target', '0')))
                                except InvalidOperation: goal['target'] = Decimal('0')
                                try: goal['current'] = Decimal(str(goal.get('current', '0')))
                                except InvalidOperation: goal['current'] = Decimal('0')
                                # Ensure dates are present, default if missing
                                goal['addedDate'] = goal.get('addedDate', datetime.datetime.min.isoformat())
                                goal['lastUpdated'] = goal.get('lastUpdated', goal['addedDate'])
                                goal['priority'] = goal.get('priority', 'medium') # Ensure priority exists

                    last_user = data.get('lastActiveUserName')
                    current_sort_criteria_cli = data.get('globalSortCriteria', 'date_desc')
                    # Automatically switch to the last user if they exist
                    if last_user and last_user in all_user_data_cli:
                        switch_user_cli(last_user, silent=True)
                    else:
                         current_user_cli = None # Ensure no user if last user doesn't exist

            except (json.JSONDecodeError, IOError, TypeError) as e:
                cli_console.print(f"[bold red]ERROR:[/bold red] Failed to load data from {CLI_DATA_FILE}. Starting fresh CLI data. Error: {e}")
                all_user_data_cli = {}
                current_user_cli = None
                current_sort_criteria_cli = 'date_desc'
            except Exception as e: # Catch unexpected errors during loading
                 cli_console.print(f"[bold red]UNEXPECTED ERROR loading CLI data:[/bold red] {e}. Starting fresh CLI data.")
                 all_user_data_cli = {}
                 current_user_cli = None
                 current_sort_criteria_cli = 'date_desc'
        else:
            cli_console.print(f"CLI data file '{CLI_DATA_FILE}' not found. Starting fresh CLI data.")
            all_user_data_cli = {}
            current_user_cli = None
            current_sort_criteria_cli = 'date_desc'


    def save_data_cli():
        """Saves the current CLI state to the JSON file."""
        if not all_user_data_cli and not current_user_cli:
             # Avoid saving an empty structure if nothing ever happened and file doesn't exist
             if os.path.exists(CLI_DATA_FILE) and not (all_user_data_cli or current_user_cli):
                 try: os.remove(CLI_DATA_FILE) # Clean up if we're effectively empty
                 except OSError: pass
             return

        try:
            # Prepare data structure, ensuring all users' goals' Decimals are stringified
            data_to_save = {
                'lastActiveUserName': current_user_cli,
                'globalSortCriteria': current_sort_criteria_cli,
                'allUserData': {}
            }
            for uname, udata in all_user_data_cli.items():
                data_to_save['allUserData'][uname] = udata.copy() # Copy user data
                if 'goals' in data_to_save['allUserData'][uname]:
                     goals_to_save_for_user = []
                     for goal in data_to_save['allUserData'][uname]['goals']:
                        goal_copy = goal.copy()
                        # Ensure conversion even if user wasn't active
                        goal_copy['target'] = str(goal_copy.get('target', Decimal('0')))
                        goal_copy['current'] = str(goal_copy.get('current', Decimal('0')))
                        goals_to_save_for_user.append(goal_copy)
                     data_to_save['allUserData'][uname]['goals'] = goals_to_save_for_user


            with open(CLI_DATA_FILE, 'w') as f:
                json.dump(data_to_save, f, indent=4)

            # Convert back to Decimal after saving for runtime use (only for current user if active)
            if current_user_cli and current_user_cli in all_user_data_cli:
                 goals_runtime = []
                 for goal in all_user_data_cli[current_user_cli]['goals']:
                     goal_copy = goal.copy()
                     goal_copy['target'] = Decimal(goal_copy['target'])
                     goal_copy['current'] = Decimal(goal_copy['current'])
                     goals_runtime.append(goal_copy)
                 all_user_data_cli[current_user_cli]['goals'] = goals_runtime


        except (IOError, TypeError) as e:
            cli_console.print(f"[bold red]ERROR:[/bold red] Failed to save CLI data to {CLI_DATA_FILE}. Error: {e}")
        except Exception as e: # Catch unexpected errors during saving
            cli_console.print(f"[bold red]UNEXPECTED ERROR saving CLI data:[/bold red] {e}")


    # --- CLI Core Logic Functions ---
    def get_current_goals_cli():
        """Returns the list of goals for the current CLI user."""
        if current_user_cli and current_user_cli in all_user_data_cli:
            # Ensure goals are Decimal objects when retrieved
            goals = all_user_data_cli[current_user_cli].get('goals', [])
            return goals # Decimals are handled during load/save

        return []

    def find_goal_cli(identifier):
        """Finds a CLI goal by ID or name (case-insensitive) for the current user."""
        goals = get_current_goals_cli()
        # Try by ID first
        for goal in goals:
            if goal.get('id') == identifier:
                return goal
        # Then try by name (case-insensitive)
        for goal in goals:
            if goal.get('name', '').lower() == identifier.lower():
                return goal
        return None

    def sort_goals_cli(goals):
        """Sorts the CLI goals list based on current_sort_criteria_cli."""
        if not goals:
            return []

        try:
            criteria, direction = current_sort_criteria_cli.split('_')
            reverse = (direction == 'desc')

            def sort_key(goal):
                target = goal.get('target', Decimal('0'))
                current = goal.get('current', Decimal('0'))
                remaining = max(Decimal('0'), target - current)
                priority_val = get_priority_value_cli(goal.get('priority'))
                added_date = datetime.datetime.min
                try:
                    added_date_str = goal.get('addedDate')
                    if added_date_str:
                        added_date = datetime.datetime.fromisoformat(added_date_str)
                except (ValueError, TypeError):
                     pass # Keep default min date if parsing fails

                if criteria == 'name':
                    return goal.get('name', '').lower()
                elif criteria == 'target':
                    return target
                elif criteria == 'remaining':
                    return remaining
                elif criteria == 'progress':
                    return (current / target) if target > 0 else Decimal('0')
                elif criteria == 'priority':
                     # Combine priority value with remaining amount for secondary sort within priority
                     # Less remaining is "better" within the same priority
                     return (priority_val, -remaining) # Minus remaining to sort smaller remaining higher
                elif criteria == 'date':
                    return added_date
                else: # Default to date
                    return added_date

            goals.sort(key=sort_key, reverse=reverse)
        except Exception as e:
             cli_console.print(f"[yellow]Warning:[/yellow] Could not sort goals: {e}")
        return goals


    def render_goals_cli():
        """Displays the current CLI user's goals in a table using rich."""
        if not current_user_cli:
            cli_console.print(Panel("[bold red]No user active in CLI.[/bold red] Use 'switch [username]' to load or create a user.", title="CLI Status", border_style="red"))
            return

        goals = get_current_goals_cli()
        if not goals:
            cli_console.print(Panel(f"No active CLI goals found for user [cyan]{current_user_cli}[/cyan]. Use 'add' command.", title="Current CLI Goals", border_style="yellow"))
            return

        sorted_goals = sort_goals_cli(list(goals)) # Sort a copy

        table = Table(title=f"CLI Goals for [cyan]{current_user_cli}[/cyan] (Sorted by: {current_sort_criteria_cli.replace('_', ' ').upper()})",
                      show_header=True, header_style="bold magenta", border_style="blue")

        table.add_column("ID", style="dim", width=10, no_wrap=True)
        table.add_column("Name", style="bold", min_width=15)
        table.add_column("Priority", style="white", width=8)
        table.add_column("Target", style="green", justify="right")
        table.add_column("Saved", style="cyan", justify="right")
        table.add_column("Remaining", style="yellow", justify="right")
        table.add_column("Progress", style="white", width=20) # Wider for progress bar
        table.add_column("Added", style="dim", width=10)

        for goal in sorted_goals:
            goal_id = goal.get('id', 'N/A')
            name = goal.get('name', 'Unnamed Goal')
            priority = (goal.get('priority', 'medium') or 'medium').upper()
            priority_style = get_priority_style_cli(priority)

            target = goal.get('target', Decimal('0'))
            current = goal.get('current', Decimal('0'))
            remaining = max(Decimal('0'), target - current)
            is_complete = current >= target and target > 0

            progress_percent = 0
            if target > 0:
                try:
                    progress_percent = min(100, int((current / target) * 100))
                except (Decimal.InvalidOperation, ZeroDivisionError):
                     progress_percent = 0 # Handle potential division by zero or invalid decimal

            # Create a Rich ProgressBar
            progress_bar_color = "green" if not is_complete else "blue"
            progress_bar = ProgressBar(total=100, completed=progress_percent, width=15, style=progress_bar_color, complete_style=progress_bar_color)
            progress_text = f"{progress_percent}%"
            progress_display = Text.assemble(progress_bar, f" {progress_text}")


            try:
                added_date_str = goal.get('addedDate')
                added_date = datetime.datetime.fromisoformat(added_date_str).strftime('%Y-%m-%d') if added_date_str else 'N/A'
            except (ValueError, TypeError):
                added_date = 'Invalid Date'


            table.add_row(
                goal_id,
                f"{name}{' [COMPLETED]' if is_complete else ''}",
                f"{priority_style}{priority}[/]",
                format_currency_cli(target),
                format_currency_cli(current),
                format_currency_cli(remaining),
                progress_display,
                added_date
            )

        cli_console.print(table)

    def add_goal_cli(name, target_str, priority):
        """Adds a new CLI goal for the current user."""
        global all_user_data_cli
        if not current_user_cli:
            cli_console.print("[bold red]ERROR:[/bold red] No user active in CLI. Use 'switch [username]' first.")
            return False

        name = name.strip()
        priority = (priority or 'medium').strip().lower()

        if not name:
            cli_console.print("[bold red]ERROR:[/bold red] Goal name cannot be empty.")
            return False
        if priority not in ['high', 'medium', 'low']:
            cli_console.print(f"[bold red]ERROR:[/bold red] Invalid priority '{priority}'. Use high, medium, or low.")
            return False

        try:
            target = Decimal(target_str)
            if target <= 0:
                cli_console.print("[bold red]ERROR:[/bold red] Target amount must be positive.")
                return False
        except InvalidOperation:
            cli_console.print(f"[bold red]ERROR:[/bold red] Invalid target amount: '{target_str}'.")
            return False

        goals = get_current_goals_cli()
        if any(g.get('name', '').lower() == name.lower() for g in goals):
            cli_console.print(f"[bold red]ERROR:[/bold red] CLI Goal named '{name}' already exists for user {current_user_cli}.")
            return False

        now = datetime.datetime.now().isoformat()
        new_goal = {
            'id': generate_id_cli(),
            'name': name,
            'target': target,
            'current': Decimal('0'),
            'priority': priority,
            'addedDate': now,
            'lastUpdated': now
        }
        all_user_data_cli.setdefault(current_user_cli, {'goals': []})['goals'].append(new_goal)
        save_data_cli()
        cli_console.print(Panel(f"✅ Added {priority.upper()} priority CLI goal '[bold cyan]{name}[/]' [Target: {format_currency_cli(target)}] for user [cyan]{current_user_cli}[/cyan].", title="CLI Goal Added", style="green", border_style="green"))
        return True

    def add_contribution_cli(identifier, amount_str):
        """Adds funds to a specific CLI goal."""
        if not current_user_cli:
            cli_console.print("[bold red]ERROR:[/bold red] No user active in CLI.")
            return False

        goal = find_goal_cli(identifier)
        if not goal:
            cli_console.print(f"[bold red]ERROR:[/bold red] CLI Goal '{identifier}' not found for user {current_user_cli}.")
            return False

        try:
            amount = Decimal(amount_str)
            if amount <= 0:
                cli_console.print("[bold red]ERROR:[/bold red] Contribution amount must be positive.")
                return False
        except InvalidOperation:
            cli_console.print(f"[bold red]ERROR:[/bold red] Invalid amount: '{amount_str}'.")
            return False

        target = goal.get('target', Decimal('0'))
        current = goal.get('current', Decimal('0'))
        is_already_complete = current >= target and target > 0

        if is_already_complete:
            cli_console.print(f"[yellow]Info:[/yellow] CLI Goal '[bold cyan]{goal['name']}[/]' is already complete. No funds added.")
            return False

        old_current = current
        goal['current'] = old_current + amount
        goal['lastUpdated'] = datetime.datetime.now().isoformat()
        new_current = goal['current']
        is_now_complete = new_current >= target and target > 0

        save_data_cli()

        remaining = max(Decimal('0'), target - new_current)
        msg = f"💰 Added {format_currency_cli(amount)} to CLI goal '[bold cyan]{goal['name']}[/]'.\n   New Balance: {format_currency_cli(new_current)}\n   Remaining: {format_currency_cli(remaining)}"
        title = "CLI Funds Added"
        style = "blue"

        if is_now_complete and not is_already_complete:
            msg += "\n   [bold green]🎉 TARGET REACHED! CONGRATULATIONS! 🎉[/bold green]"
            title = "CLI Goal Completed!"
            style = "bold green"

        cli_console.print(Panel(msg, title=title, style=style, border_style=style))
        return True


    def delete_goal_cli(identifier):
        """Deletes a CLI goal after confirmation."""
        global all_user_data_cli
        if not current_user_cli:
            cli_console.print("[bold red]ERROR:[/bold red] No user active in CLI.")
            return False

        goal = find_goal_cli(identifier)
        if not goal:
            cli_console.print(f"[bold red]ERROR:[/bold red] CLI Goal '{identifier}' not found for user {current_user_cli}.")
            return False

        goal_name = goal.get('name', 'N/A')
        goal_id = goal.get('id', 'N/A')
        goal_priority = (goal.get('priority', 'N/A')).upper()
        goal_current = format_currency_cli(goal.get('current', Decimal('0')))

        cli_console.print(Panel(f"User: [cyan]{current_user_cli}[/]\nCLI Goal: '[bold cyan]{goal_name}[/]' (ID: {goal_id})\nPriority: {get_priority_style_cli(goal_priority)}{goal_priority}[/]\nSaved: {goal_current}", title="Confirm CLI Deletion", border_style="bold red", style="yellow"))

        if Confirm.ask(f"❓ Permanently delete CLI goal '[bold cyan]{goal_name}[/]'?", default=False):
            goals = get_current_goals_cli()
            goals[:] = [g for g in goals if g.get('id') != goal_id] # Filter out the goal
            save_data_cli()
            cli_console.print(Panel(f"🗑️ CLI Goal '[bold cyan]{goal_name}[/]' deleted for user [cyan]{current_user_cli}[/cyan].", title="CLI Deletion Complete", style="green", border_style="green"))
            return True
        else:
            cli_console.print("[yellow]CLI Deletion cancelled.[/yellow]")
            return False


    def switch_user_cli(username, silent=False):
        """Switches the active CLI user, loading or creating their data."""
        global current_user_cli, all_user_data_cli
        new_username = username.strip().upper()
        if not new_username:
            cli_console.print("[bold red]ERROR:[/bold red] Username cannot be empty.")
            return

        if current_user_cli == new_username:
            if not silent:
                cli_console.print(f"[yellow]Already managing CLI goals for user [cyan]{current_user_cli}[/cyan].[/yellow]")
            return

        # Save current user's data before switching
        if current_user_cli and current_user_cli in all_user_data_cli:
             save_data_cli() # Save will handle string conversion temporarily

        current_user_cli = new_username
        # Load/initialize new user's data
        if current_user_cli not in all_user_data_cli:
            all_user_data_cli[current_user_cli] = {'goals': []}
            if not silent:
                cli_console.print(f"✨ Created new CLI user profile for [cyan]{current_user_cli}[/cyan].")
        else:
             # Ensure goals are loaded as Decimal if switching back
             goals_runtime = []
             for goal in all_user_data_cli[current_user_cli].get('goals',[]):
                 goal_copy = goal.copy()
                 try: goal_copy['target'] = Decimal(str(goal_copy.get('target', '0')))
                 except InvalidOperation: goal_copy['target'] = Decimal('0')
                 try: goal_copy['current'] = Decimal(str(goal_copy.get('current', '0')))
                 except InvalidOperation: goal_copy['current'] = Decimal('0')
                 goal_copy['priority'] = goal_copy.get('priority', 'medium')
                 goal_copy['addedDate'] = goal_copy.get('addedDate', datetime.datetime.min.isoformat())
                 goal_copy['lastUpdated'] = goal_copy.get('lastUpdated', goal_copy['addedDate'])
                 goals_runtime.append(goal_copy)
             all_user_data_cli[current_user_cli]['goals'] = goals_runtime

        if not silent:
            cli_console.print(f"👤 Switched to CLI user: [bold cyan]{current_user_cli}[/bold cyan]")

        save_data_cli() # Save the switch (updates lastActiveUserName)

    def get_summary_cli():
        """Calculates and prints a summary for the current CLI user."""
        if not current_user_cli:
            cli_console.print("[bold red]ERROR:[/bold red] No user active in CLI.")
            return

        goals = get_current_goals_cli()
        total_goals = len(goals)
        completed_goals = sum(1 for g in goals if g.get('current', Decimal('0')) >= g.get('target', Decimal('0')) and g.get('target', Decimal('0')) > 0)
        total_saved = sum(g.get('current', Decimal('0')) for g in goals)
        total_target = sum(g.get('target', Decimal('0')) for g in goals)
        total_remaining = sum(max(Decimal('0'), g.get('target', Decimal('0')) - g.get('current', Decimal('0'))) for g in goals)

        prio_counts = {'high': 0, 'medium': 0, 'low': 0}
        for g in goals:
            prio = (g.get('priority', 'medium') or 'medium').lower()
            if prio in prio_counts:
                prio_counts[prio] += 1

        summary_text = f"""\
[bold]CLI Goal Summary for [cyan]{current_user_cli}[/cyan]:[/bold]
---------------------------------
Total Goals:    [bold]{total_goals}[/] ({completed_goals} complete)
Priorities:     [bold red]{prio_counts['high']} High[/] / [bold yellow]{prio_counts['medium']} Medium[/] / [dim green]{prio_counts['low']} Low[/]
Total Saved:    [bold cyan]{format_currency_cli(total_saved)}[/]
Total Target:   [green]{format_currency_cli(total_target)}[/]
Total Remaining:[bold yellow]{format_currency_cli(total_remaining)}[/]
"""
        cli_console.print(Panel(summary_text, title="CLI Summary", border_style="blue"))


    def export_goals_cli():
         """Exports current CLI user's goals to JSON format displayed on console."""
         if not current_user_cli:
            cli_console.print("[bold red]ERROR:[/bold red] No user active in CLI.")
            return
         goals = get_current_goals_cli()
         if not goals:
              cli_console.print(f"[yellow]No CLI goals to export for user [cyan]{current_user_cli}[/cyan].[/yellow]")
              return

         export_data = []
         for goal in goals:
            goal_copy = goal.copy()
            # Ensure Decimals are strings for export display
            goal_copy['target'] = str(goal_copy.get('target', '0'))
            goal_copy['current'] = str(goal_copy.get('current', '0'))
            export_data.append(goal_copy)

         try:
             json_string = json.dumps(export_data, indent=2)
             cli_console.print(Panel(json_string, title=f"CLI Goal Export for [cyan]{current_user_cli}[/cyan] (JSON)", border_style="magenta"))
         except (TypeError, Exception) as e:
             cli_console.print(f"[bold red]ERROR:[/bold red] Failed to generate export data: {e}")


    # --- CLI Command Processing ---
    def process_command_cli(command):
        """Parses and executes user commands for CLI."""
        global current_sort_criteria_cli
        parts = command.strip().split() # Use strip() before split()
        if not parts:
            return True # Continue loop

        cmd = parts[0].lower() # Process command in lower case
        args = parts[1:]

        # Commands that don't require a user
        if cmd in ['help', '?']:
            cli_console.print("""
[bold magenta]Available CLI Commands:[/bold magenta]
  [cyan]list / ls[/cyan]           - Show goals for the current user (respects sort order).
  [cyan]add[/cyan] [i]name target priority[/i] - Add a new goal (e.g., add "Vacation Fund" 50000 high). Priority is optional (defaults medium). Names with spaces MUST be in quotes.
  [cyan]fund[/cyan] [i]id/name amount[/i] - Add funds to a goal (e.g., fund "Vacation Fund" 500 or fund abc123xyz 500). Names with spaces MUST be in quotes.
  [cyan]delete[/cyan] [i]id/name[/i]    - Delete a goal (requires confirmation). Names with spaces MUST be in quotes.
  [cyan]switch[/cyan] [i]username[/i]  - Switch to/create another user profile. Usernames with spaces MUST be in quotes.
  [cyan]summary[/cyan]           - Show a summary of goals for the current user.
  [cyan]sort[/cyan] [i]criteria_direction[/i] - Change goal sorting (e.g., sort priority_desc, sort name_asc).
        Criteria: [yellow]name, target, remaining, progress, priority, date[/yellow]
        Directions: [yellow]asc, desc[/yellow]
  [cyan]user[/cyan]               - Show the current active user.
  [cyan]export[/cyan]            - Display current user's goals data as JSON.
  [cyan]help / ?[/cyan]          - Show this help message.
  [cyan]exit / quit / q[/cyan]    - Exit the application.
""")
        elif cmd in ['exit', 'quit', 'q']:
            cli_console.print("[bold blue]Exiting Savings Tracker CLI. Goodbye![/bold blue]")
            return False # Stop loop
        elif cmd == 'switch':
            if not args:
                cli_console.print("[bold red]Usage:[/bold red] switch [username] (use quotes for names with spaces)")
            else:
                 # Reconstruct potential quoted argument
                 potential_username = command.strip()[len('switch'):].strip()
                 if potential_username.startswith('"') and potential_username.endswith('"'):
                      username_to_switch = potential_username[1:-1]
                 else:
                      username_to_switch = potential_username # Allow single-word unquoted

                 if not username_to_switch:
                      cli_console.print("[bold red]ERROR:[/bold red] Username cannot be empty.")
                 else:
                      switch_user_cli(username_to_switch)
        elif cmd == 'user':
             if current_user_cli:
                 cli_console.print(f"Current active CLI user: [bold cyan]{current_user_cli}[/]")
             else:
                 cli_console.print("[yellow]No CLI user is currently active.[/yellow]")

        # Commands requiring a user
        elif not current_user_cli:
            cli_console.print("[bold red]No user active in CLI.[/bold red] Please use 'switch [username]' first.")

        elif cmd in ['list', 'ls']:
            render_goals_cli()
        elif cmd == 'add':
            # Usage: add <name> <target> [priority]
            # Need custom parsing for name with spaces
            cmd_parts = command.strip().split(maxsplit=1) # Split off 'add'
            if len(cmd_parts) < 2:
                cli_console.print("[bold red]Usage:[/bold red] add \"<Goal Name>\" <target> [priority (high/medium/low)]")
                cli_console.print("       Example: add \"New Laptop\" 120000 medium")
                return True

            arg_string = cmd_parts[1].strip()
            name = None
            remaining_args_string = arg_string

            # Check for quoted name
            if arg_string.startswith('"'):
                 end_quote_index = arg_string.find('"', 1) # Find closing quote after the first one
                 if end_quote_index != -1:
                      name = arg_string[1:end_quote_index]
                      remaining_args_string = arg_string[end_quote_index + 1:].strip()
                 else:
                      cli_console.print("[bold red]Syntax Error:[/bold red] Unclosed quote in goal name. Use \"<Goal Name>\".")
                      return True
            else:
                 # No quotes, assume first word is name (until space)
                 name_parts = remaining_args_string.split(maxsplit=1)
                 name = name_parts[0]
                 if len(name_parts) > 1:
                     remaining_args_string = name_parts[1].strip()
                 else:
                     remaining_args_string = "" # No args after the single word name

            remaining_parts = remaining_args_string.split()

            if not name or len(remaining_parts) < 1:
                 cli_console.print("[bold red]Usage:[/bold red] add \"<Goal Name>\" <target> [priority (high/medium/low)]")
                 cli_console.print("       Example: add \"New Laptop\" 120000 medium")
                 cli_console.print("       Example (single word name): add CarFund 500000 high")
                 return True

            target_str = remaining_parts[0]
            priority = remaining_parts[1] if len(remaining_parts) > 1 else 'medium'

            add_goal_cli(name, target_str, priority)

        elif cmd == 'fund':
            # Usage: fund <id_or_name> <amount>
            cmd_parts = command.strip().split(maxsplit=1) # Split off 'fund'
            if len(cmd_parts) < 2:
                cli_console.print("[bold red]Usage:[/bold red] fund \"<Goal Name or ID>\" <amount>")
                cli_console.print("       Example: fund \"Vacation Fund\" 500")
                cli_console.print("       Example: fund abc123xyz 500")
                return True

            arg_string = cmd_parts[1].strip()
            identifier = None
            amount_str = None

            # Check for quoted identifier (name with spaces)
            if arg_string.startswith('"'):
                 end_quote_index = arg_string.find('"', 1)
                 if end_quote_index != -1:
                      identifier = arg_string[1:end_quote_index]
                      remaining_args_string = arg_string[end_quote_index + 1:].strip()
                      remaining_parts = remaining_args_string.split()
                      if len(remaining_parts) > 0:
                           amount_str = remaining_parts[0]
                      else:
                          cli_console.print("[bold red]Syntax Error:[/bold red] Amount missing after quoted goal name/ID.")
                          return True
                 else:
                      cli_console.print("[bold red]Syntax Error:[/bold red] Unclosed quote in goal name/ID. Use \"<Goal Name or ID>\".")
                      return True
            else:
                 # No quotes, assume first word is identifier
                 identifier_parts = arg_string.split(maxsplit=1)
                 if len(identifier_parts) == 2:
                     identifier = identifier_parts[0]
                     amount_str = identifier_parts[1]
                 else:
                     cli_console.print("[bold red]Usage:[/bold red] fund <goal_id_or_name> <amount> (use quotes for names with spaces)")
                     return True

            if identifier and amount_str:
                 add_contribution_cli(identifier, amount_str)
            else:
                 cli_console.print("[bold red]Syntax Error:[/bold red] Invalid format. Usage: fund \"<Goal Name or ID>\" <amount>")


        elif cmd == 'delete':
            # Usage: delete <id_or_name>
            cmd_parts = command.strip().split(maxsplit=1) # Split off 'delete'
            if len(cmd_parts) < 2:
                cli_console.print("[bold red]Usage:[/bold red] delete \"<Goal Name or ID>\" (use quotes for names with spaces)")
                return True

            identifier_string = cmd_parts[1].strip()
            identifier = None

            # Check for quoted identifier
            if identifier_string.startswith('"') and identifier_string.endswith('"'):
                 identifier = identifier_string[1:-1]
            elif ' ' not in identifier_string:
                 identifier = identifier_string # Allow single-word unquoted
            else:
                 cli_console.print("[bold red]Syntax Error:[/bold red] Goal name/ID with spaces must be in quotes. Usage: delete \"<Goal Name>\" or delete <GoalID>")
                 return True

            if identifier:
                 delete_goal_cli(identifier)
            else:
                 cli_console.print("[bold red]Syntax Error:[/bold red] Goal name or ID is missing.")


        elif cmd == 'summary':
            get_summary_cli()
        elif cmd == 'sort':
            if not args:
                cli_console.print(f"Current sort order: [yellow]{current_sort_criteria_cli}[/yellow]")
                cli_console.print("Usage: sort <criteria_direction> (e.g., sort priority_desc)")
            else:
                new_sort = args[0].lower()
                valid_criteria = ['name', 'target', 'remaining', 'progress', 'priority', 'date']
                valid_directions = ['asc', 'desc']
                try:
                    crit, direction = new_sort.split('_')
                    if crit in valid_criteria and direction in valid_directions:
                        current_sort_criteria_cli = new_sort
                        save_data_cli()
                        cli_console.print(f"Sorting changed to: [yellow]{current_sort_criteria_cli}[/yellow]")
                        #render_goals_cli() # Optionally re-render after sort
                    else:
                        cli_console.print(f"[bold red]Invalid sort option:[/bold red] '{new_sort}'. Use criteria: {valid_criteria}, directions: {valid_directions}.")
                except ValueError:
                     cli_console.print(f"[bold red]Invalid sort format:[/bold red] '{new_sort}'. Use format 'criteria_direction' (e.g., name_asc).")
        elif cmd == 'export':
             export_goals_cli()
        else:
            cli_console.print(f"[bold red]Unknown command:[/bold red] '{cmd}'. Type 'help' for options.")

        return True # Continue loop

    # --- CLI Main Application Loop ---
    def main_cli():
        """Runs the interactive CLI application."""
        load_data_cli()
        cli_console.print(Panel("[bold green]SAVINGS GOAL TRACKER [5153] - CLI Edition[/bold green]\nType 'help' for commands.", title="CLI Welcome", border_style="green"))

        if not current_user_cli:
             cli_console.print("[yellow]No user loaded in CLI. Use 'switch [username]' to begin.[/yellow]")
             # Optional: Prompt for username if none loaded
             # initial_user = Prompt.ask("Enter username to load or create", default=None)
             # if initial_user:
             #     switch_user_cli(initial_user)

        while True:
            try:
                user_prompt = f"([cyan]{current_user_cli if current_user_cli else 'NO USER'}[/cyan] CLI) > "
                command = Prompt.ask(user_prompt)
                if not process_command_cli(command):
                    break # Exit command was entered
            except (KeyboardInterrupt, EOFError): # Handle Ctrl+C and Ctrl+D
                cli_console.print("\n[yellow]Exiting CLI.[/yellow]")
                break
            except Exception as e:
                 cli_console.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
                 cli_console.print("[yellow]Attempting to continue CLI session. Please save important data if possible ('save').[/yellow] (Note: 'save' is automatic on exit and goal changes)")


        save_data_cli() # Ensure data is saved on exit
        cli_console.print("[dim]CLI Data saved.[/dim]")
else:
    # Define a stub for main_cli if rich isn't available
    def main_cli():
        print("CLI mode requires the 'rich' library. Please install it (`pip install rich`).")


# --- Main Execution Block (Handles API Server Start or CLI Mode) ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Savings Tracker Backend API Server & CLI Tool.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="By default, runs the FastAPI web server. Use --cli for the interactive terminal mode, or --create-user for API user management."
    )
    parser.add_argument(
        "--create-user",
        metavar="USERNAME",
        help="Create a new user and generate an API key for the API backend (uses database). Server and CLI will NOT start.",
        type=str
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run the interactive CLI application (uses local JSON file). Server will NOT start."
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="[API MODE] Host address to bind the server to (default: 127.0.0.1)."
    )
    parser.add_argument(
        "--port",
        default=8000,
        type=int,
        help="[API MODE] Port to run the server on (default: 8000)."
    )

    args = parser.parse_args()

    if args.create_user:
        if FASTAPI_AVAILABLE and DB_SETUP_SUCCESS:
            username_to_create = args.create_user
            # Basic validation aligned with Pydantic schema
            if not username_to_create or len(username_to_create) < 3 or len(username_to_create) > 50:
                 print("Error: Username must be between 3 and 50 characters long.", file=sys.stderr)
            elif re and not re.match("^[A-Z0-9_-]+$", username_to_create.upper()):
                 print("Error: Username can only contain uppercase letters, numbers, underscores, and hyphens.", file=sys.stderr)
            else:
                add_user_and_key_logic(username_to_create)
        elif not FASTAPI_AVAILABLE:
             print("API mode dependencies (FastAPI, SQLAlchemy, etc.) are not installed. Cannot create user.", file=sys.stderr)
        elif not DB_SETUP_SUCCESS:
            print("Database connection failed during setup. Cannot create user.", file=sys.stderr)

    elif args.cli:
        if RICH_AVAILABLE:
             main_cli()
        else:
             main_cli() # Call the stub which prints the error message

    else:
        if FASTAPI_AVAILABLE and DB_SETUP_SUCCESS:
             # Create tables if they don't exist before starting server
            print("Checking/creating database tables for API...")
            try:
                Base.metadata.create_all(bind=engine)
                print("Database tables checked/created.")
            except Exception as e:
                print(f"[bold red]Error during API database table creation:[/bold red] {e}", file=sys.stderr, style="bold red")
                # The API will still start, but endpoints requiring tables will fail.
                # Decide if you want to sys.exit(1) here instead.
                pass # Allow server to start even without tables for / and /health

            print(f"Starting Savings Tracker API server on http://{args.host}:{args.port}")
            if app.docs_url:
                print(f"Access API docs at http://{args.host}:{args.port}{app.docs_url}")
            else:
                 print("[yellow]Interactive API docs disabled due to database setup issues.[/yellow]")
            try:
                 uvicorn.run(app, host=args.host, port=args.port)
            except Exception as e:
                 print(f"[bold red]Error starting Uvicorn server:[/bold red] {e}", file=sys.stderr, style="bold red")

        elif not FASTAPI_AVAILABLE:
            print("API mode dependencies (FastAPI, SQLAlchemy, etc.) are not installed.", file=sys.stderr)
            print("Please install them (`pip install 'fastapi[all]' sqlalchemy python-dotenv passlib[bcrypt] uvicorn[standard]`) to run the API server.", file=sys.stderr)
        elif not DB_SETUP_SUCCESS:
             print("Database connection failed during API setup. Cannot start API server with functional endpoints.", file=sys.stderr)
             # You could optionally try to run a minimal API here if needed,
             # but the current code just prints the error and finishes if not running CLI/create-user.
             # Or run the app with limited endpoints:
             # print("Starting minimal API server (endpoints requiring DB will not work)...")
             # try:
             #      uvicorn.run(app, host=args.host, port=args.port)
             # except Exception as e:
             #      print(f"[bold red]Error starting minimal Uvicorn server:[/bold red] {e}", file=sys.stderr, style="bold red")
