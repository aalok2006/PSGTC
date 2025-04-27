# To run this code you need to install the following dependencies:
# pip install Flask google-genai

import os
# import base64 # base64 is not used in this Flask app version
from flask import Flask, request, jsonify, render_template_string
from google import genai
from google.genai import types

# Initialize Flask app
app = Flask(__name__)

# --- Google GenAI Setup ---
# Check if API key is set
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("CRITICAL ERROR: GEMINI_API_KEY environment variable not set.")
    print("Please set the environment variable before running the app.")
    # Store None if key is missing, so the /chat route can check
    app.config['GENAI_CLIENT'] = None
else:
    try:
        genai_client = genai.Client(api_key=api_key)
        # Optional: Test connectivity (might add startup delay)
        # print("Google GenAI client initialized. Testing connectivity...")
        # try:
        #     models = list(genai_client.models.list())
        #     print(f"Successfully listed {len(models)} models.")
        # except Exception as e:
        #     print(f"Warning: Failed to list GenAI models. API key might be invalid or lack permissions. Error: {e}")
        app.config['GENAI_CLIENT'] = genai_client
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to initialize Google GenAI client: {e}")
        print("Please check your GEMINI_API_KEY.")
        app.config['GENAI_CLIENT'] = None # Ensure it's None on failure

# --- HTML Content as a Python String ---
# The entire HTML, CSS, and JavaScript is stored here
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Add unique identifier to title for clarity -->
    <title>PERSONALIZED SAVINGS GOAL TRACKER [5153] - User Specific</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" integrity="sha512-9usAa10IRO0HhonpyAIVpjrylPvoDwiPUiKdWk5t3PyolY1cOd4DSE0Ga+ri4AuTroPR5aQvXU9xC6qOPnzFeg==" crossorigin="anonymous" referrerpolicy="no-referrer" />

    <style>
        :root {
            --monitor-bg: #0a0a0a;
            --monitor-fg: #00ff41;
            --monitor-fg-dim: #00802b;
            --monitor-fg-accent: #33ff77;
            --monitor-border: var(--monitor-fg-dim);
            --danger-color: #ff4100; /* Also used for High priority */
            --font-family: "Monospac821 BT", Consolas, Monaco, "Andale Mono", "Ubuntu Mono", monospace;
            --transition-speed: 0.15s ease;
            --cmatrix-bg-alpha: 0.05; /* Slightly adjusted alpha */
            --cmatrix-font-size: 14px;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            border-radius: 0 !important; /* Keep the sharp corners */
        }

        html {
            scroll-behavior: smooth;
        }

        body {
            font-family: var(--font-family);
            background-color: var(--monitor-bg);
            color: var(--monitor-fg);
            line-height: 1.6;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            text-shadow: 0 0 3px rgba(0, 255, 65, 0.3);
            overflow-x: hidden; /* Prevent horizontal scroll */
        }

        #cmatrix-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            pointer-events: none;
            opacity: 0.8; /* Maintain visibility */
        }

        /* Scanlines effect */
        body::before {
            content: " ";
            display: block;
            position: fixed;
            top: 0; left: 0; bottom: 0; right: 0;
            width: 100%; height: 100%;
            z-index: 0;
            pointer-events: none;
            background: repeating-linear-gradient(
                0deg,
                rgba(0, 0, 0, 0) 0px,
                rgba(0, 0, 0, 0) 1px,
                rgba(0, 0, 0, 0.15) 2px, /* Subtle scanlines */
                rgba(0, 0, 0, 0.15) 3px
            );
            opacity: 0.7;
        }


        main {
            flex-grow: 1;
            padding: 15px;
            max-width: 900px;
            margin: 15px auto;
            width: 95%;
            border: 1px solid var(--monitor-border);
            background-color: rgba(10, 10, 10, 0.85); /* Slightly transparent background */
            position: relative;
            z-index: 1;
        }

        header {
            background: var(--monitor-bg);
            color: var(--monitor-fg);
            padding: 1rem 0;
            text-align: center;
            border-bottom: 2px solid var(--monitor-fg);
            margin-bottom: 15px;
            text-transform: uppercase;
            position: relative;
            z-index: 1;
        }

        header h1 {
            font-weight: normal;
            letter-spacing: 2px;
            font-size: 1.5rem;
        }

        /* --- User Greeting and Edit Button --- */
        #user-greeting {
            font-weight: normal;
            display: inline-block;
            border-bottom: 1px dashed var(--monitor-fg-dim);
        }
         #edit-name-btn {
            font-size: 0.8em;
            margin-left: 8px;
            cursor: pointer;
            opacity: 0.7;
            transition: opacity var(--transition-speed);
            display: inline-block; /* Changed from none */
            vertical-align: middle;
        }
        #edit-name-btn:hover {
            opacity: 1;
            color: var(--monitor-fg-accent);
        }
        #edit-name-btn.hidden { /* Keep hidden class functional */
             display: none !important;
        }
        /* NEW: Style for when no user is set */
        #user-greeting.no-user {
            color: var(--danger-color);
            border-bottom-color: var(--danger-color);
        }


        h2 {
            color: var(--monitor-fg);
            margin-bottom: 15px;
            font-weight: normal;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 1.2rem;
            border-bottom: 1px solid var(--monitor-border);
            padding-bottom: 5px;
            display: block; /* Explicitly block */
        }

        .card {
            background-color: transparent;
            border: 1px solid var(--monitor-border);
            padding: 15px;
            margin-bottom: 20px;
            transition: border-color var(--transition-speed);
        }

        .card:hover { /* Subtle hover */
             border-color: var(--monitor-fg-accent);
             transform: none; /* Disable any scaling/translation */
             box-shadow: none; /* Disable any shadow */
        }
        /* --- Goal Completion Flash --- */
        .card.goal-complete-flash {
             border-color: var(--monitor-fg) !important;
             box-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
             transition: border-color 0.1s ease-in, box-shadow 0.1s ease-in;
        }

        .btn {
            display: inline-block;
            padding: 8px 15px;
            border: 1px solid var(--monitor-fg);
            background-color: var(--monitor-fg);
            color: var(--monitor-bg);
            cursor: pointer;
            font-weight: normal;
            transition: background-color var(--transition-speed), color var(--transition-speed), border-color var(--transition-speed);
            text-align: center;
            font-size: 0.95rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-family: var(--font-family);
            user-select: none; /* Prevent text selection */
             -webkit-user-select: none;
             -moz-user-select: none;
        }

        .btn:hover {
            background-color: var(--monitor-fg-accent);
            border-color: var(--monitor-fg-accent);
            color: var(--monitor-bg);
            transform: none; /* No transform */
        }
        .btn:active { /* Active state feedback */
             background-color: var(--monitor-fg-dim);
             border-color: var(--monitor-fg-dim);
        }
        .btn:disabled { /* Disabled state */
            opacity: 0.5;
            cursor: not-allowed;
            background-color: var(--monitor-fg-dim);
             border-color: var(--monitor-fg-dim);
        }

        .btn-primary {} /* Placeholder if needed */
        .btn-secondary {} /* Placeholder if needed */

        .btn-danger {
            background-color: var(--danger-color);
            border-color: var(--danger-color);
            color: var(--monitor-bg);
            padding: 8px 12px; /* Slightly smaller */
        }
        .btn-danger:hover {
            background-color: var(--monitor-bg); /* Invert on hover */
            border-color: var(--danger-color);
            color: var(--danger-color);
        }

        .form-group {
            margin-bottom: 15px;
        }

        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: normal;
            color: var(--monitor-fg);
            text-transform: uppercase;
            font-size: 0.9em;
        }

        .form-group input[type="text"],
        .form-group input[type="number"],
        .form-group select, /* Added select styling */
        .contribution-input { /* Shared input styles */
            width: 100%;
            padding: 8px;
            border: 1px solid var(--monitor-border);
            font-size: 1rem;
            background-color: var(--monitor-bg);
            color: var(--monitor-fg);
            font-family: var(--font-family);
            transition: border-color var(--transition-speed), box-shadow var(--transition-speed);
        }
        .form-group input:focus,
        .form-group select:focus, /* Added focus for select */
        .contribution-input:focus {
            outline: none;
            border-color: var(--monitor-fg-accent);
            box-shadow: 0 0 5px rgba(0, 255, 65, 0.5); /* Subtle glow on focus */
        }

        /* Remove number input spinners */
        input[type=number]::-webkit-inner-spin-button,
        input[type=number]::-webkit-outer-spin-button {
          -webkit-appearance: none;
          margin: 0;
        }
        input[type=number] {
          -moz-appearance: textfield;
        }

         /* --- Goals Header with Sort Controls --- */
         .goals-header {
             display: flex;
             justify-content: space-between;
             align-items: flex-end; /* Align bottom */
             flex-wrap: wrap; /* Allow wrapping on small screens */
             margin-bottom: 10px;
             border-bottom: 1px solid var(--monitor-border);
             padding-bottom: 5px;
         }
         .goals-header h2 {
             margin-bottom: 0; /* Remove bottom margin */
             border-bottom: none; /* Remove double border */
             padding-bottom: 0;
         }
         .sort-controls {
             display: flex;
             gap: 8px;
             align-items: center;
              margin-top: 5px; /* Space when wrapped */
         }
         .sort-controls label {
             font-size: 0.85em;
             text-transform: uppercase;
             color: var(--monitor-fg-dim); /* Dim label */
         }
         .sort-controls select {
             background-color: var(--monitor-bg);
             color: var(--monitor-fg);
             border: 1px solid var(--monitor-border);
             padding: 4px 6px;
             font-family: var(--font-family);
             font-size: 0.85em;
             cursor: pointer;
         }
        .sort-controls select:focus {
             outline: none;
             border-color: var(--monitor-fg-accent);
             box-shadow: 0 0 4px rgba(0, 255, 65, 0.4);
         }


        .goals-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); /* Responsive grid */
            gap: 20px;
            margin-top: 15px;
        }

        .goal-card {
            display: flex;
            flex-direction: column; /* Stack elements vertically */
        }

        .goal-card h3 {
            color: var(--monitor-fg);
            margin-bottom: 10px;
            font-size: 1.1rem;
            font-weight: normal;
            border-bottom: 1px dashed var(--monitor-border);
            padding-bottom: 5px;
            text-transform: uppercase;
            word-break: break-word; /* Prevent long names overflowing */
        }

        .goal-card p {
            margin-bottom: 6px;
            font-size: 0.9rem;
            color: var(--monitor-fg);
        }
        .goal-card .goal-target,
        .goal-card .goal-current {
            font-weight: normal; /* Ensure consistent weight */
        }
        .goal-card .goal-remaining {
            color: var(--danger-color); /* Danger color for remaining */
            font-style: normal; /* Not italic */
            margin-bottom: 10px;
        }
        /* --- Goal Meta Info (Date Added & Priority) --- */
        .goal-card .goal-meta {
            font-size: 0.75em;
            color: var(--monitor-fg-dim);
            margin-top: 5px;
            text-transform: uppercase;
        }
        .goal-card .goal-priority {
            font-size: 0.8em;
            text-transform: uppercase;
            margin-top: 5px; /* Space it out */
            margin-bottom: 5px;
        }
        .goal-priority .priority-label { color: var(--monitor-fg-dim); }
        .goal-priority .priority-value { font-weight: normal; /* Keep consistent weight */ }
        .goal-priority .priority-high { color: var(--danger-color); } /* Red for High */
        .goal-priority .priority-medium { color: var(--monitor-fg-accent); } /* Accent Green for Medium */
        .goal-priority .priority-low { color: var(--monitor-fg-dim); } /* Dim Green for Low */


        .progress-container {
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
            border: 1px solid var(--monitor-border); /* Border around progress */
            padding: 2px;
        }

        progress {
            flex-grow: 1;
            appearance: none;
            -webkit-appearance: none;
            -moz-appearance: none; /* Remove default styles */
            height: 14px;
            overflow: hidden;
            border: none; /* Remove default border */
            background-color: var(--monitor-bg); /* Match background */
        }
        /* Style the progress bar track */
        progress::-webkit-progress-bar { background-color: var(--monitor-bg); }
        /* Style the progress bar value */
        progress::-moz-progress-bar { background-color: var(--monitor-fg); transition: none; } /* No transition for FF */
        progress::-webkit-progress-value { background-color: var(--monitor-fg); transition: none; } /* No transition for Webkit */

        .progress-text {
            font-weight: normal;
            color: var(--monitor-fg);
            font-size: 0.9rem;
            min-width: 45px; /* Ensure space for "100%" */
            text-align: right;
            white-space: nowrap; /* Prevent wrapping */
        }

        .goal-actions {
            margin-top: auto; /* Push actions to the bottom */
            padding-top: 10px;
            border-top: 1px solid var(--monitor-border);
            display: flex;
            gap: 8px;
            align-items: center;
            flex-wrap: wrap; /* Allow wrapping */
        }

        .contribution-input {
            flex-grow: 1; /* Take available space */
            padding: 8px;
            min-width: 70px; /* Minimum width */
            max-width: 120px; /* Maximum width */
            font-size: 0.9rem;
        }

        footer {
            text-align: center;
            padding: 10px;
            margin-top: 20px;
            color: var(--monitor-fg-dim);
            font-size: 0.85rem;
            border-top: 1px solid var(--monitor-border);
            text-transform: uppercase;
            letter-spacing: 1px;
            position: relative;
            z-index: 1;
        }

        .hidden { display: none !important; }

        #no-goals-message {
            text-align: center;
            color: var(--monitor-fg-dim);
            font-style: normal; /* Not italic */
            margin-top: 25px;
            padding: 15px;
            border: 1px dashed var(--monitor-border);
        }
        /* NEW: Message for when no user is set */
        #no-user-message {
            text-align: center;
            color: var(--danger-color);
            font-style: normal;
            margin-top: 25px;
            padding: 15px;
            border: 1px dashed var(--danger-color);
            font-weight: bold;
        }


        /* --- Chatbot FAB --- */
        #chatbot-fab {
            position: fixed;
            bottom: 20px;
            /* Adjust right position to avoid overlapping with new credit line if needed */
            /* Example: right: 240px; (Needs testing) */
            /* Or leave as is if overlap is acceptable/minor */
            right: 20px;
            width: 50px;
            height: 50px;
            background: var(--monitor-fg);
            color: var(--monitor-bg);
            border: 1px solid var(--monitor-fg);
            font-size: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: transform 0.2s ease-out, background-color 0.2s ease-out;
            z-index: 1000;
        }
        #chatbot-fab:hover {
            background: var(--monitor-fg-accent);
            border-color: var(--monitor-fg-accent);
            transform: scale(1.05); /* Slight scale on hover */
        }
        #chatbot-fab i { font-style: normal !important; /* Override potential italic from FA */ }

        /* --- Chatbot Container --- */
        #chatbot-container {
            position: fixed;
            bottom: 80px; /* Position above FAB */
            right: 20px;
            width: 350px;
            max-width: 90vw;
            height: 480px;
            max-height: 75vh;
            background-color: rgba(10, 10, 10, 0.9); /* Semi-transparent */
            border: 2px solid var(--monitor-fg);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            z-index: 999;
            transform: translateY(20px) scale(0.95); /* Start slightly down and scaled */
            opacity: 0;
            visibility: hidden;
            transition: transform 0.2s ease-out, opacity 0.2s ease-out, visibility 0.2s;
        }
        #chatbot-container.active { /* Active state */
            transform: translateY(0) scale(1);
            opacity: 1;
            visibility: visible;
        }

        #chatbot-header {
            background: var(--monitor-fg);
            color: var(--monitor-bg);
            padding: 8px 12px;
            font-weight: normal;
            display: flex;
            justify-content: space-between;
            align-items: center;
            text-transform: uppercase;
            letter-spacing: 1px;
            cursor: default; /* Default cursor for header */
        }

        #chatbot-close-btn {
            background: none; border: none;
            color: var(--monitor-bg);
            font-size: 22px; cursor: pointer;
            opacity: 0.9; font-family: sans-serif; /* Consistent close button */
            padding: 0 5px; line-height: 1;
        }
        #chatbot-close-btn:hover { opacity: 1; color: #000; } /* Darken on hover */

        #chatbot-messages {
            flex-grow: 1;
            padding: 12px;
            overflow-y: auto; /* Enable scrolling */
            background-color: rgba(0, 0, 0, 0.3); /* Darker message area */
            border-top: 1px solid var(--monitor-border);
            border-bottom: 1px solid var(--monitor-border);
        }
        /* --- Custom Scrollbar for Chat --- */
        #chatbot-messages::-webkit-scrollbar { width: 6px; }
        #chatbot-messages::-webkit-scrollbar-track { background: var(--monitor-bg); }
        #chatbot-messages::-webkit-scrollbar-thumb { background-color: var(--monitor-fg-dim); border: 1px solid var(--monitor-bg); }
        #chatbot-messages::-webkit-scrollbar-thumb:hover { background-color: var(--monitor-fg); }

        .chat-message {
            margin-bottom: 12px; padding: 8px 12px;
            border: 1px solid var(--monitor-border);
            max-width: 90%; /* Prevent full width messages */
            word-wrap: break-word; /* Wrap long words */
            font-size: 0.9rem; line-height: 1.5;
            /* --- Animation setup --- */
            animation-duration: 0.3s;
            animation-timing-function: ease-out;
            animation-fill-mode: forwards;
            opacity: 0; /* Start hidden */
        }
        .chat-message.user {
            background-color: var(--monitor-bg);
            border-color: var(--monitor-fg-dim); /* Dim border for user */
            margin-left: auto; /* Align right */ color: var(--monitor-fg);
            text-align: right;
             /* animation-name handled by JS now */
        }
        .chat-message.bot {
            background-color: var(--monitor-bg);
            border-color: var(--monitor-border);
            margin-right: auto; /* Align left */ color: var(--monitor-fg);
             /* animation-name handled by JS now */
        }
        /* --- Chat Message Formatting --- */
         .chat-message strong {
            font-weight: normal; color: var(--monitor-fg-accent);
            text-decoration: underline; text-decoration-color: var(--monitor-fg-dim);
         }
         .chat-message code {
             background-color: rgba(0, 255, 65, 0.1); /* Slight background for code */
             padding: 1px 4px; font-size: 0.85em;
             border: 1px solid var(--monitor-fg-dim);
         }
         .chat-message ul {
             list-style-type: '- '; /* Custom list bullet */ margin-left: 15px; margin-top: 5px;
             text-align: left; /* Ensure lists are left-aligned */
         }
         .chat-message li { margin-bottom: 3px; }
         .chat-message pre { /* Style for preformatted text (like JSON export) */
            background-color: rgba(0,0,0,0.5);
            border: 1px dashed var(--monitor-fg-dim);
            padding: 8px;
            margin-top: 5px;
            font-size: 0.8em;
            white-space: pre-wrap; /* Wrap lines */
            word-break: break-all; /* Break long strings */
            max-height: 150px; /* Limit height */
            overflow-y: auto; /* Scroll if needed */
            text-align: left;
         }

        #chatbot-input-container {
            display: flex; padding: 10px;
            background-color: var(--monitor-bg);
        }
        #chatbot-input {
            flex-grow: 1; padding: 8px;
            border: 1px solid var(--monitor-border); margin-right: 8px;
            font-size: 0.9rem; background-color: var(--monitor-bg);
            color: var(--monitor-fg); font-family: var(--font-family);
        }
        #chatbot-input:focus {
            outline: none; border-color: var(--monitor-fg-accent);
            box-shadow: 0 0 4px rgba(0, 255, 65, 0.4);
        }
        #chatbot-send-btn {
            padding: 8px 12px; font-size: 0.9rem;
            min-width: 40px; /* Ensure minimum size */ display: flex;
            align-items: center; justify-content: center;
        }
        #chatbot-send-btn i { font-style: normal !important; font-size: 1em; line-height: 1;}


        /* --- Animations --- */
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes fadeOut { from { opacity: 1; } to { opacity: 0; } }
        @keyframes slideInBot {
          from { transform: translateX(-15px); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideInUser {
          from { transform: translateX(15px); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }

        .animate-on-load { animation: fadeIn 0.5s ease-out forwards; opacity: 0; }
        .animate-add { animation: fadeIn 0.4s ease-out forwards; }
        .animate-delete { animation: fadeOut 0.4s ease-in forwards; }


        /* --- Responsive Design --- */
        @media (max-width: 768px) {
            body { font-size: 14px; }
            header h1 { font-size: 1.3rem; }
            main { width: 98%; padding: 10px; margin: 10px auto;}
            .goals-container { grid-template-columns: 1fr; gap: 15px; }
             .goals-header { flex-direction: column; align-items: flex-start; } /* Stack header items */
             .sort-controls { width: 100%; justify-content: flex-end; } /* Move sort to right */
            .card { padding: 12px; }
            .goal-actions { flex-direction: column; align-items: stretch; } /* Stack goal actions */
            .contribution-input { max-width: none; width: 100%; }
            .btn { width: 100%; } /* Full width buttons in goal actions */
            .btn-danger { width: auto; align-self: flex-end; } /* Except delete */

            #chatbot-container { width: 95vw; bottom: 70px; right: 2.5vw; height: 400px; }
            #chatbot-fab { bottom: 15px; right: 15px; width: 45px; height: 45px; font-size: 20px; }
        }

        @media (max-width: 480px) {
            body { font-size: 13px; }
            header h1 { font-size: 1.1rem; letter-spacing: 1px; }
            h2 { font-size: 1rem; }
            .goal-card h3 { font-size: 1rem; }
            .btn { padding: 10px 12px; font-size: 0.9rem; }
            .goal-card p { font-size: 0.85rem; }
            .progress-text { font-size: 0.85rem; min-width: 40px;}
             #chatbot-container { height: 65vh; }
             .chat-message { font-size: 0.85rem; max-width: 92%; }
             #chatbot-input { font-size: 0.85rem; }
             #chatbot-send-btn { padding: 8px 10px; font-size: 0.85rem;}
             /* Stack sort controls neatly on smallest screens */
             .sort-controls { flex-direction: column; align-items: flex-end; gap: 5px;}
             .sort-controls label { width: 100%; text-align: right;}
             .sort-controls select { width: auto; } /* Allow select to size itself */
        }

        /* --- Style for the Creator Credit --- */
        #creator-credit {
            position: fixed; /* Position relative to the viewport */
            bottom: 5px;    /* Small space from the bottom edge */
            right: 10px;   /* Small space from the right edge */
            color: var(--monitor-fg-dim); /* Use the dim monitor color */
            font-family: var(--font-family); /* Match the font */
            font-size: 0.75em; /* Make it small */
            text-transform: uppercase; /* Match footer style */
            letter-spacing: 0.5px; /* Match footer style */
            text-shadow: 0 0 2px rgba(0, 255, 65, 0.15); /* Subtle shadow */
            z-index: 5; /* Above main content/scanlines, below chat FAB */
            pointer-events: none; /* Prevent it from being clickable */
            user-select: none; /* Prevent text selection */
            -webkit-user-select: none;
            -moz-user-select: none;
        }

    </style>
</head>
<body>

    <canvas id="cmatrix-bg"></canvas>

    <header>
        <h1>
            <!-- Updated Greeting structure -->
            [ <span id="user-greeting">NO USER</span>'S SAVINGS GOALS ]
            <span id="edit-name-btn" class="hidden" title="Switch User">[SWITCH]</span>
        </h1>
    </header>

    <main>
        <section class="add-goal-section card animate-on-load">
            <h2>> ADD NEW GOAL_</h2>
            <form id="goal-form">
                <div class="form-group">
                    <label for="goal-name">GOAL NAME:</label>
                    <input type="text" id="goal-name" required maxlength="100">
                </div>
                <div class="form-group">
                    <label for="goal-target">TARGET AMOUNT (₹):</label> <!-- Currency Change -->
                    <input type="number" id="goal-target" min="0.01" step="any" required>
                </div>
                <!-- NEW Priority Field -->
                <div class="form-group">
                     <label for="goal-priority">PRIORITY:</label>
                     <select id="goal-priority">
                         <option value="high">HIGH</option>
                         <option value="medium" selected>MEDIUM</option>
                         <option value="low">LOW</option>
                     </select>
                 </div>
                <button type="submit" class="btn btn-primary">ADD GOAL</button>
            </form>
        </section>

        <section class="goals-display-section">
             <div class="goals-header">
                <h2>> CURRENT GOALS_</h2>
                <div class="sort-controls">
                     <label for="sort-select">SORT BY:</label>
                     <select id="sort-select">
                         <option value="date_desc">DATE ADDED (NEW-OLD)</option>
                         <option value="date_asc">DATE ADDED (OLD-NEW)</option>
                         <option value="priority_desc">PRIORITY (HIGH-LOW)</option> <!-- Added Priority Sort -->
                         <option value="priority_asc">PRIORITY (LOW-HIGH)</option> <!-- Added Priority Sort -->
                         <option value="name_asc">NAME (A-Z)</option>
                         <option value="name_desc">NAME (Z-A)</option>
                         <option value="target_asc">TARGET (LOW-HIGH)</option>
                         <option value="target_desc">TARGET (HIGH-LOW)</option>
                         <option value="remaining_asc">REMAINING (LOW-HIGH)</option>
                         <option value="remaining_desc">REMAINING (HIGH-LOW)</option>
                         <option value="progress_desc">PROGRESS (% DESC)</option>
                         <option value="progress_asc">PROGRESS (% ASC)</option>
                     </select>
                </div>
            </div>
            <div id="goals-list" class="goals-container">
                <!-- Goals are dynamically added here -->
            </div>
            <!-- Modified no goals message -->
            <p id="no-goals-message" class="hidden">NO ACTIVE GOALS FOUND FOR THIS USER. USE FORM ABOVE OR CHAT COMMAND <code>add goal</code>.</p>
            <!-- NEW Message for when no user is loaded -->
            <p id="no-user-message" class="hidden">NO USER LOADED. PLEASE <a href="#" id="set-initial-user-link">SET USER IDENTIFIER</a> TO VIEW OR ADD GOALS.</p>
        </section>
    </main>

    <footer>
        <p>PERSONALIZED SAVINGS GOAL TRACKER // SYSTEM READY [5153]</p>
    </footer>

    <button id="chatbot-fab" title="Chat Assistant">
         <i class="fa-solid fa-terminal"></i>
    </button>

    <div id="chatbot-container">
        <div id="chatbot-header">
            <span>ASSISTANCE CHATBOT</span>
            <button id="chatbot-close-btn" title="Close Assistant">×</button>
        </div>
        <div id="chatbot-messages">
            <!-- Chat messages go here -->
        </div>
        <div id="chatbot-input-container">
            <input type="text" id="chatbot-input" placeholder="INPUT COMMAND...">
            <button id="chatbot-send-btn" class="btn btn-primary" title="Send Message">
                 <i class="fa-solid fa-paper-plane"></i>
            </button>
        </div>
    </div>

    <!-- ****** ADDED CREATOR CREDIT LINE HERE ****** -->
    <div id="creator-credit">CREATED BY: AALOK KUMAR YADAV</div>
    <!-- ******************************************** -->


    <script>
        document.addEventListener('DOMContentLoaded', () => {
            // --- DOM Element References ---
            const goalForm = document.getElementById('goal-form');
            const goalNameInput = document.getElementById('goal-name');
            const goalTargetInput = document.getElementById('goal-target');
            const goalPrioritySelect = document.getElementById('goal-priority'); // Added priority select
            const goalsList = document.getElementById('goals-list');
            const noGoalsMessage = document.getElementById('no-goals-message');
            const noUserMessage = document.getElementById('no-user-message');
            const setInitialUserLink = document.getElementById('set-initial-user-link');
            const userGreeting = document.getElementById('user-greeting');
            const editNameBtn = document.getElementById('edit-name-btn');
            const sortSelect = document.getElementById('sort-select');

            const chatbotFab = document.getElementById('chatbot-fab');
            const chatbotContainer = document.getElementById('chatbot-container');
            const chatbotCloseBtn = document.getElementById('chatbot-close-btn');
            const chatbotMessages = document.getElementById('chatbot-messages');
            const chatbotInput = document.getElementById('chatbot-input');
            const chatbotSendBtn = document.getElementById('chatbot-send-btn');

            const canvas = document.getElementById('cmatrix-bg');
            const ctx = canvas.getContext('2d');

            // --- State Variables ---
            let goals = []; // This now holds the *active* user's goals
            let userName = ''; // Currently active user
            let allUserData = {}; // Object to store data for ALL users { 'USERNAME': { goals: [...], ... }, ... }
            let currentSortCriteria = 'date_desc'; // Global sort preference
            let matrixInterval;

            // NEW Versioned key for the updated structure
            const LOCAL_STORAGE_KEY = 'savingsTrackerData_IBM5153_v3_UserSpecific';

            // --- Utility Functions ---
            const formatCurrency = (amount) => {
                // Currency Change: GBP to INR
                return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(amount);
            };

            const generateId = () => `_${Math.random().toString(36).substr(2, 9)}`;

            const escapeHTML = (str) => {
                 if (str === null || str === undefined) return '';
                 const div = document.createElement('div');
                 div.appendChild(document.createTextNode(String(str)));
                 return div.innerHTML;
            };

            // --- Data Persistence ---
            const saveDataToLocalStorage = () => {
                try {
                    if (userName && allUserData[userName]) {
                        allUserData[userName].goals = [...goals];
                    } else if (userName) {
                         allUserData[userName] = { goals: [...goals] };
                    }

                    const data = {
                        lastActiveUserName: userName,
                        allUserData: allUserData,
                        globalSortCriteria: currentSortCriteria
                    };
                    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(data));
                } catch (e) {
                    console.error("SYSTEM WARNING: Failed to save data to localStorage:", e);
                    displayMessage("SYSTEM WARNING: Failed to save data. Local storage might be full or disabled.", 'bot');
                }
            };

            const loadDataFromLocalStorage = () => {
                const storedData = localStorage.getItem(LOCAL_STORAGE_KEY);
                if (storedData) {
                    try {
                        const data = JSON.parse(storedData);
                        allUserData = data.allUserData || {};
                        const lastUser = data.lastActiveUserName || '';
                        currentSortCriteria = data.globalSortCriteria || 'date_desc';
                        sortSelect.value = currentSortCriteria;
                        switchUser(lastUser, false); // Switch to the last user, don't save immediately

                    } catch (e) {
                        console.error("ERROR: Could not parse localStorage data:", e);
                        allUserData = {}; userName = ''; goals = []; currentSortCriteria = 'date_desc';
                        localStorage.removeItem(LOCAL_STORAGE_KEY);
                        alert("ERROR: Could not load saved data. Data seems corrupted and has been reset.");
                        displayMessage("CRITICAL ERROR: Corrupted save data detected and reset. Previous data lost.", 'bot');
                        // Removed force prompt on load, rely on UI message
                        // promptForName(true); // Force prompt if data was corrupt
                    }
                } else {
                    allUserData = {}; userName = ''; goals = []; currentSortCriteria = 'date_desc';
                }
            };

            // --- UI Update Functions ---
            const updateGreeting = () => {
                const safeUserName = escapeHTML(userName);
                if (userName) {
                    userGreeting.textContent = `${safeUserName}`;
                    userGreeting.classList.remove('no-user');
                    editNameBtn.classList.remove('hidden');
                    goalForm.style.opacity = '1';
                    goalForm.querySelectorAll('input, select, button').forEach(el => el.disabled = false); // Include select
                    goalsList.classList.remove('hidden');
                    noUserMessage.classList.add('hidden');
                    noGoalsMessage.classList.add('hidden'); // Hide no goals message initially when user is set, renderGoals handles showing it

                } else {
                    userGreeting.textContent = 'NO USER';
                    userGreeting.classList.add('no-user');
                    editNameBtn.classList.add('hidden');
                    goalForm.style.opacity = '0.5';
                    goalForm.querySelectorAll('input, select, button').forEach(el => el.disabled = true); // Include select
                    goalsList.classList.add('hidden');
                    noGoalsMessage.classList.add('hidden');
                    noUserMessage.classList.remove('hidden');
                }
                 // Update chat context *after* setting the user/state
                if (chatbotContainer.classList.contains('active')) {
                     setTimeout(updateChatbotContext, 100);
                }
            };

             // --- Function to handle switching users ---
             const switchUser = (newUserName, shouldSave = true) => {
                const oldUserName = userName;
                newUserName = newUserName ? newUserName.trim().toUpperCase() : '';

                if (oldUserName && allUserData[oldUserName] && shouldSave) {
                    allUserData[oldUserName].goals = [...goals];
                } else if (oldUserName && shouldSave) { // Handle case where user might exist but goals property doesn't
                    allUserData[oldUserName] = allUserData[oldUserName] || {};
                    allUserData[oldUserName].goals = [...goals];
                }

                userName = newUserName;

                if (userName && allUserData[userName]) {
                    // Ensure goals property exists and is an array
                    allUserData[userName].goals = Array.isArray(allUserData[userName].goals) ? allUserData[userName].goals : [];
                    goals = allUserData[userName].goals.map(g => ({
                        ...g,
                        current: Number(g.current) || 0,
                        target: Number(g.target) || 0,
                        priority: g.priority || 'medium', // Load priority, default to medium
                        addedDate: g.addedDate || new Date(0).toISOString(),
                        lastUpdated: g.lastUpdated || g.addedDate || new Date(0).toISOString()
                    }));
                } else if (userName) {
                    allUserData[userName] = { goals: [] };
                    goals = [];
                } else {
                    goals = []; // No user means no goals loaded
                }

                updateGreeting(); // This also updates chat context if open
                renderGoals();

                if (shouldSave) {
                    saveDataToLocalStorage();
                     // Alert only if it's a user-initiated switch that changes the user
                    if (oldUserName !== userName) {
                         // No alert needed if chatbot provides feedback
                    }
                }
                 // Chatbot feedback is now handled within updateGreeting's updateChatbotContext call
             };

            const promptForName = (force = false) => {
                const promptMessage = force
                    ? `SWITCH USER\nENTER USER IDENTIFIER [CURRENT: ${userName || 'NONE'}]:`
                    : `SYSTEM REQUIRES USER IDENTIFICATION.\nENTER NAME TO LOAD/CREATE PROFILE:`;
                const currentNameToSuggest = userName || '';

                const nameInput = prompt(promptMessage, currentNameToSuggest);

                if (nameInput !== null) {
                    const trimmedName = nameInput.trim(); // Allow mixed case temporarily for comparison
                    if (trimmedName && trimmedName.length > 0 && trimmedName.length <= 50) { // Added length check
                         const trimmedNameUpper = trimmedName.toUpperCase();
                         if (trimmedNameUpper !== userName) {
                              switchUser(trimmedNameUpper);
                              // Feedback message is handled by updateGreeting -> updateChatbotContext
                         } else {
                             if (chatbotContainer.classList.contains('active')) {
                                 displayMessage(`SYSTEM: USER IDENTIFIER IS ALREADY <strong>${escapeHTML(userName)}</strong>. NO CHANGE MADE.`, 'bot', true);
                             } else {
                                alert(`User identifier is already "${userName}". No change made.`);
                             }
                         }
                    } else if (!trimmedName && force && userName) {
                         // Prompt was cancelled or empty, and there was an existing user - do nothing
                          if (chatbotContainer.classList.contains('active')) {
                             displayMessage(`SYSTEM: User switch cancelled or empty name provided. Current user <strong>${escapeHTML(userName)}</strong> remains active.`, 'bot', true);
                          } else {
                            alert("User switch cancelled or name cannot be empty.");
                          }

                    } else if (!trimmedName && !userName) {
                        // Prompt was cancelled or empty, and no user was active
                        if (chatbotContainer.classList.contains('active')) {
                             displayMessage(`SYSTEM ERROR: USER IDENTIFIER REQUIRED. Please enter a valid name to begin tracking goals.`, 'bot', true);
                        } else {
                            alert("USER IDENTIFIER REQUIRED: Please enter a valid name to begin.");
                        }
                         // Keep the UI in the 'no user' state
                         updateGreeting(); renderGoals();
                    } else if (trimmedName.length > 50) {
                        if (chatbotContainer.classList.contains('active')) {
                             displayMessage(`SYSTEM ERROR: USER IDENTIFIER TOO LONG (MAX 50 CHARACTERS).`, 'bot', true);
                        } else {
                             alert("USER IDENTIFIER TOO LONG (MAX 50 CHARACTERS).");
                        }
                    }
                } else {
                     // User cancelled the prompt
                    if (force && userName && chatbotContainer.classList.contains('active')) {
                         displayMessage(`SYSTEM: User switch cancelled. Current user <strong>${escapeHTML(userName)}</strong> remains active.`, 'bot', true);
                    } else if (force && !userName && chatbotContainer.classList.contains('active')) {
                         displayMessage(`SYSTEM: User identification cancelled. No user loaded.`, 'bot', true);
                    }
                     // If prompt cancelled and no user active, ensure UI stays in 'no user' state
                     if (!userName) { updateGreeting(); renderGoals(); }
                }
            };


            // --- Goal Sorting Logic ---
            const sortGoals = () => {
                if (!Array.isArray(goals)) {
                    console.error("Sort error: goals is not an array for user:", userName);
                    goals = [];
                    return;
                }
                const [criteria, direction] = currentSortCriteria.split('_');
                // Priority mapping: High > Medium > Low
                const priorityMap = { high: 3, medium: 2, low: 1 };

                goals.sort((a, b) => {
                     let valA, valB;
                     switch (criteria) {
                         case 'name': valA = a.name.toLowerCase(); valB = b.name.toLowerCase(); break;
                         case 'target': valA = Number(a.target); valB = Number(b.target); break;
                         case 'remaining': valA = Math.max(0, Number(a.target) - Number(a.current)); valB = Math.max(0, Number(b.target) - Number(b.current)); break;
                         case 'progress': valA = Number(a.target) > 0 ? (Math.min(Number(a.current), Number(a.target)) / Number(a.target)) : 0; valB = Number(b.target) > 0 ? (Math.min(Number(b.current), Number(b.target)) / Number(b.target)) : 0; break;
                         // Added Priority Sorting
                         case 'priority':
                             valA = priorityMap[a.priority?.toLowerCase()] || 0; // Default to 0 if missing/invalid
                             valB = priorityMap[b.priority?.toLowerCase()] || 0;
                             break;
                         case 'date': default: valA = new Date(a.addedDate); valB = new Date(b.addedDate); break;
                     }
                     let comparison = 0;
                     if (valA > valB) comparison = 1; else if (valA < valB) comparison = -1;

                     // Special handling for date ascending: oldest first (standard asc)
                     // For others, asc means lowest value first, desc means highest value first.
                     // Date desc means newest first, asc means oldest first.
                     if (criteria === 'date') {
                          return direction === 'desc' ? (comparison * -1) : comparison; // Newest first (desc), Oldest first (asc)
                     } else if (criteria === 'priority') {
                         return direction === 'desc' ? (comparison * -1) : comparison; // High first (desc), Low first (asc)
                     } else {
                          // For numerical/alphabetical sorts (name, target, remaining, progress)
                         return direction === 'asc' ? comparison : (comparison * -1);
                     }
                 });
            };


            // --- Goal Rendering ---
            const renderGoals = () => {
                 if (!userName) {
                    goalsList.innerHTML = '';
                    noGoalsMessage.classList.add('hidden');
                    noUserMessage.classList.remove('hidden');
                    goalsList.classList.add('hidden'); // Hide the container itself
                    return;
                 }

                 noUserMessage.classList.add('hidden'); // Hide no user message when user is set
                 sortGoals(); // Sort before rendering
                 goalsList.innerHTML = ''; // Clear current list

                 if (goals.length === 0) {
                     noGoalsMessage.classList.remove('hidden');
                     goalsList.classList.add('hidden'); // Keep container hidden if no goals
                 } else {
                     noGoalsMessage.classList.add('hidden');
                     goalsList.classList.remove('hidden'); // Show container if there are goals
                     goals.forEach(goal => {
                         const goalElement = createGoalElement(goal);
                         goalsList.appendChild(goalElement);
                          // Add animation class only to *newly* added elements on screen if needed,
                          // but for re-rendering the whole list, simple append is fine.
                          // Add 'rendered' class to mark them as present
                          goalElement.classList.add('rendered');
                     });
                      // Removed the explicit animation timeout loop as it's for new adds, not full render
                 }
            };

            const createGoalElement = (goal) => {
                const card = document.createElement('div');
                card.classList.add('goal-card', 'card');
                card.dataset.id = goal.id;

                const progressValue = Math.max(0, Math.min(Number(goal.current), Number(goal.target)));
                const progressPercent = Number(goal.target) > 0 ? Math.round((progressValue / Number(goal.target)) * 100) : 0;
                const remaining = Math.max(0, Number(goal.target) - Number(goal.current));
                const isComplete = Number(goal.current) >= Number(goal.target) && Number(goal.target) > 0;
                const addedDateStr = goal.addedDate ? new Date(goal.addedDate).toLocaleDateString('en-GB') : 'N/A';
                const priorityClass = `priority-${goal.priority || 'medium'}`; // Default class if needed
                const priorityText = (goal.priority || 'medium').toUpperCase(); // Default text

                card.innerHTML = `
                    <h3>${escapeHTML(goal.name)} ${isComplete ? '[COMPLETE]' : ''}</h3>
                    <p class="goal-target">TARGET: ${formatCurrency(goal.target)}</p>
                    <div class="progress-container">
                        <progress value="${progressValue}" max="${goal.target}"></progress>
                        <span class="progress-text">${progressPercent}%</span>
                    </div>
                    <p class="goal-current">SAVED: ${formatCurrency(goal.current)}</p>
                    <p class="goal-remaining">REMAINING: ${formatCurrency(remaining)}</p>
                    <!-- Display Priority -->
                    <p class="goal-priority">
                        <span class="priority-label">PRIORITY:</span> <span class="priority-value ${priorityClass}">${escapeHTML(priorityText)}</span>
                    </p>
                    <p class="goal-meta">ADDED: ${addedDateStr}</p>
                    <div class="goal-actions">
                        <input type="number" class="contribution-input" placeholder="ADD ₹" min="0.01" step="any" aria-label="Add funds to ${escapeHTML(goal.name)}" ${isComplete ? 'disabled' : ''}> <!-- Currency Change -->
                        <button class="btn btn-secondary btn-add-contribution" ${isComplete ? 'disabled' : ''}>ADD FUNDS</button>
                        <button class="btn btn-danger btn-delete-goal">DELETE</button>
                    </div>
                `;

                const addButton = card.querySelector('.btn-add-contribution');
                const deleteButton = card.querySelector('.btn-danger.btn-delete-goal'); // More specific selector
                const contributionInputEl = card.querySelector('.contribution-input');

                if (!isComplete) {
                    // Ensure previous listeners are removed if this is an update
                    const oldAddButton = card.querySelector('.btn-add-contribution');
                     if (oldAddButton) oldAddButton.replaceWith(addButton); // Replace to remove old listeners
                     const oldInput = card.querySelector('.contribution-input');
                     if (oldInput) oldInput.replaceWith(contributionInputEl); // Replace input too

                    addButton.addEventListener('click', () => handleAddContribution(goal.id, card));
                    contributionInputEl.addEventListener('keypress', (e) => {
                        if (e.key === 'Enter') { e.preventDefault(); handleAddContribution(goal.id, card); }
                    });
                } else {
                     // Ensure disabled state is correctly reflected and listeners removed
                     if (addButton) addButton.disabled = true;
                     if (contributionInputEl) contributionInputEl.disabled = true;
                }

                 // Ensure previous listeners are removed for delete button
                 const oldDeleteButton = card.querySelector('.btn-danger.btn-delete-goal');
                 if (oldDeleteButton) oldDeleteButton.replaceWith(deleteButton); // Replace to remove old listeners
                deleteButton.addEventListener('click', () => handleDeleteGoal(goal.id, card));


                return card;
            };

             const updateGoalElement = (goalId) => {
                 const goal = goals.find(g => g.id === goalId);
                 if (!goal) return;
                 let card = goalsList.querySelector(`.goal-card[data-id="${goalId}"]`);

                 if (card) {
                     // Create a new element with updated data
                     const updatedCardElement = createGoalElement(goal);

                      // Replace the old card with the new one to update content and re-attach listeners
                     card.replaceWith(updatedCardElement);

                      // Trigger a subtle visual update animation/flash
                      const updatedCard = goalsList.querySelector(`.goal-card[data-id="${goalId}"]`); // Get the newly added card
                      if(updatedCard) {
                          updatedCard.style.transition = 'none'; // Disable transition temporarily
                          updatedCard.style.borderColor = 'var(--monitor-fg-accent)';
                          updatedCard.style.boxShadow = '0 0 8px rgba(51, 255, 119, 0.4)';
                          // Force reflow to apply immediate style change before transition
                          void updatedCard.offsetWidth;
                           updatedCard.style.transition = 'border-color 0.3s ease-in-out, box-shadow 0.3s ease-in-out'; // Re-enable transition
                          setTimeout(() => {
                              if (updatedCard && updatedCard.style) { // Check if card still exists
                                  updatedCard.style.borderColor = ''; updatedCard.style.boxShadow = '';
                              }
                          }, 300);

                           // If goal is newly completed, add the flash animation
                           if (goal.current >= goal.target && goal.target > 0 && updatedCard.querySelector('.btn-add-contribution').disabled) {
                                updatedCard.classList.add('goal-complete-flash');
                                setTimeout(() => updatedCard.classList.remove('goal-complete-flash'), 1000);
                           }
                      }

                 } else {
                      renderGoals(); // Fallback: re-render all goals if single update fails
                  }
             };


            // --- Core Goal Logic Handlers ---
            const handleAddGoal = (name, target, priority) => { // Added priority parameter
                 if (!userName) {
                    alert("ACTION FAILED: No user is active. Please set user identifier first.");
                    // Removed automatic prompt, user should use UI elements
                    // promptForName(true);
                    return false;
                 }

                 name = name.trim();
                 target = parseFloat(target);
                 priority = priority || 'medium'; // Default priority if somehow null/undefined

                 if (!name || isNaN(target) || target <= 0) {
                     alert('INPUT ERROR: VALID GOAL NAME AND POSITIVE TARGET AMOUNT REQUIRED.'); return false;
                 }
                 if (goals.some(g => g.name.toLowerCase() === name.toLowerCase())) {
                     alert(`INPUT ERROR: Goal named "${escapeHTML(name)}" already exists for user ${userName}.`); return false;
                 }
                 if (name.length > 100) {
                     alert('INPUT ERROR: GOAL NAME TOO LONG (MAX 100 CHARACTERS).'); return false;
                 }

                const now = new Date().toISOString();
                const newGoal = {
                    id: generateId(),
                    name: name,
                    target: target,
                    current: 0,
                    priority: priority, // Save priority
                    addedDate: now,
                    lastUpdated: now
                };
                goals.push(newGoal);
                saveDataToLocalStorage();
                renderGoals(); // Re-render to show the new goal in sorted order

                 if (chatbotContainer.classList.contains('active')) {
                      displayMessage(`OK. New <strong>${priority.toUpperCase()}</strong> priority goal "<strong>${escapeHTML(name)}</strong>" [Target: ${formatCurrency(target)}] added for user <strong>${escapeHTML(userName)}</strong>.`, 'bot', true);
                 }

                return true;
            };

            const handleAddContribution = (goalId, cardElement) => {
                 const contributionInput = cardElement.querySelector('.contribution-input');
                 const amount = parseFloat(contributionInput.value);

                if (isNaN(amount) || amount <= 0) {
                    alert('INPUT ERROR: VALID POSITIVE AMOUNT REQUIRED.');
                    contributionInput.value = ''; contributionInput.focus(); return;
                }

                 const goalIndex = goals.findIndex(g => g.id === goalId);
                 if (goalIndex > -1) {
                     const goal = goals[goalIndex];
                     const oldCurrent = goal.current;
                     goal.current = Math.round((oldCurrent + amount) * 100) / 100; // Handle floating point errors
                     goal.lastUpdated = new Date().toISOString();
                     const wasCompleted = oldCurrent < goal.target && goal.current >= goal.target;

                     saveDataToLocalStorage();
                     updateGoalElement(goalId); // Update only the single goal element
                     contributionInput.value = ''; // Clear input after successful add
                     contributionInput.blur(); // Remove focus

                     if (chatbotContainer.classList.contains('active')) {
                         let message = `OK. <strong>${formatCurrency(amount)}</strong> ADDED TO "<strong>${escapeHTML(goal.name)}</strong>".<br>New balance: ${formatCurrency(goal.current)}.`;
                         if (wasCompleted) {
                            message += `<br><strong>TARGET REACHED! CONGRATULATIONS, ${escapeHTML(userName)}!</strong>`;
                         } else {
                             const remaining = Math.max(0, goal.target - goal.current);
                             message += ` Remaining: ${formatCurrency(remaining)}.`;
                         }
                         displayMessage(message, 'bot', true);
                     }
                 } else {
                     alert('ERROR: Goal not found for current user. Please refresh.');
                     if (chatbotContainer.classList.contains('active')) { displayMessage(`CRITICAL ERROR: Could not find goal ID ${goalId} for contribution for user ${userName}.`, 'bot'); }
                 }
            };

            const handleDeleteGoal = (goalId, cardElement = null) => {
                 const goalIndex = goals.findIndex(g => g.id === goalId);
                 if (goalIndex === -1) return false;

                 const goal = goals[goalIndex];
                 const deletedGoalName = goal.name;

                 if (!confirm(`CONFIRM DELETION\n----------------\nUSER: ${userName}\nGOAL: "${escapeHTML(goal.name)}"\nSAVED: ${formatCurrency(goal.current)}\nPRIORITY: ${goal.priority?.toUpperCase() || 'N/A'}\n\nTHIS ACTION CANNOT BE UNDONE. PROCEED?`)) {
                      if (chatbotContainer.classList.contains('active')) {
                         displayMessage(`ACTION CANCELLED: Deletion of goal "<strong>${escapeHTML(deletedGoalName)}</strong>" for user <strong>${escapeHTML(userName)}</strong> aborted.`, 'bot', true);
                      }
                     return false; // User cancelled
                 }


                 if (!cardElement) { cardElement = goalsList.querySelector(`.goal-card[data-id="${goalId}"]`); }

                 if (cardElement) {
                     cardElement.classList.remove('animate-add');
                     cardElement.classList.add('animate-delete');
                     cardElement.addEventListener('animationend', () => {
                         cardElement.remove();
                         if (goals.length === 0) { noGoalsMessage.classList.remove('hidden'); goalsList.classList.add('hidden'); }
                         else { renderGoals(); } // Re-render to update list & sorting if needed
                     }, { once: true });
                 }

                 goals.splice(goalIndex, 1);
                 saveDataToLocalStorage();

                 // If element wasn't animated or removed, check empty state immediately
                 if (!cardElement || !cardElement.classList.contains('animate-delete')) {
                     if (goals.length === 0) { noGoalsMessage.classList.remove('hidden'); goalsList.classList.add('hidden'); }
                     else if (!cardElement) { renderGoals(); } // If card wasn't found, re-render list
                 }


                 if (chatbotContainer.classList.contains('active')) {
                     displayMessage(`OK. Goal "<strong>${escapeHTML(deletedGoalName)}</strong>" deleted for user <strong>${escapeHTML(userName)}</strong>.`, 'bot', true);
                 }
                 return true;
            };


            // --- Chatbot Functions ---
            const toggleChatbot = () => {
                const isActive = chatbotContainer.classList.toggle('active');
                if (isActive) {
                     updateChatbotContext();
                     if (chatbotMessages.children.length === 0) {
                           displayMessage("SYSTEM BOOT COMPLETE. TRACKER [5153] ONLINE. ASSISTANCE CHATBOT READY.", "bot");
                           // context message added by updateChatbotContext call above
                     }
                     chatbotInput.focus();
                }
            };

            const updateChatbotContext = () => {
                // Only update context if chatbot is open
                if (!chatbotContainer.classList.contains('active')) return;

                let contextMessage = "";
                let useHtml = false; // Keep it simple, plain text context is fine
                if (userName) {
                    const safeUserName = escapeHTML(userName);
                    contextMessage = `CURRENT USER: ${safeUserName}. Commands will affect this user's goals saved locally. Type 'help' for options.`;
                } else {
                    contextMessage = "NO USER ACTIVE. Please use the '[SWITCH]' button or 'change name [username]' command to set a user profile.";
                }
                // Check if the last message is already the context message to avoid repetition
                const lastMessage = chatbotMessages.lastElementChild;
                 // Simple check: does the last message contain the current context string?
                 if (!lastMessage || !lastMessage.textContent.includes(contextMessage.replace(/<\/?strong>/g, ''))) { // Remove HTML tags for check
                     // Add a slight delay to ensure it appears after potential boot message
                     setTimeout(() => displayMessage(contextMessage, 'bot', true), lastMessage ? 50 : 500); // Small delay if last message exists, longer if empty
                }
            };


            const displayMessage = (text, sender, isRawHtml = false) => {
                if (!text && !isRawHtml) return; // Don't display empty messages unless they are raw html

                const messageElement = document.createElement('div');
                messageElement.classList.add('chat-message', sender);
                if (isRawHtml) { messageElement.innerHTML = text; }
                else { messageElement.textContent = text; } // Default to textContent for safety

                // Apply animation after adding to DOM
                chatbotMessages.appendChild(messageElement);
                // Use a small timeout to ensure element is added and can receive animation
                setTimeout(() => {
                     messageElement.style.animationName = sender === 'user' ? 'slideInUser' : 'slideInBot';
                     messageElement.style.opacity = 1; // Set final opacity for forwards fill mode
                }, 10);


                // Auto-scroll to bottom
                chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
            };

                        // --- Client-Side Command Handling ---
            // These commands are handled purely in JavaScript based on the local goal data
            const processClientSideCommand = (userInputLower, userInputRaw, safeUserName) => {
                let response = "";
                let isHtml = false;
                let commandHandled = true; // Assume handled unless no match

                // Commands that require a user
                const userRequiredCommands = [
                    "list goals", "ls", "summary", "total saved", "total remaining",
                    "progress", "status", "remaining", "left for", "closest goal",
                    "export goals", // Existing
                    "list complete goals", "list incomplete goals", "list high priority goals", // New list filters
                    "list medium priority goals", "list low priority goals", // New list filters
                    "goal details", "check goal", // New goal specifics
                    "count goals", "count complete goals", "count incomplete goals", // New counts
                    "count high priority goals", "count medium priority goals", "count low priority goals" // New priority counts
                ];
                 const requiresUser = userRequiredCommands.some(cmd => userInputLower === cmd || (cmd.endsWith(" ") && userInputLower.startsWith(cmd))); // Check exact match OR startsWith for commands needing arguments

                if (requiresUser && !userName) {
                    response = `ERROR: No user active. Please set a user first using the '[SWITCH]' button or <code>change name [username]</code> command to manage goals.`;
                    isHtml = true;
                } else if (userInputLower.startsWith("change name ")) {
                     const newName = userInputRaw.substring("change name ".length).trim();
                     if (newName && newName.length > 0 && newName.length <= 50) {
                         const newNameUpper = newName.trim().toUpperCase();
                         if (newNameUpper !== userName) {
                             switchUser(newNameUpper);
                             response = `SYSTEM: User switched to <strong>${escapeHTML(userName)}</strong>.`; isHtml = true;
                         } else {
                             response = `SYSTEM: USER IDENTIFIER IS ALREADY <strong>${escapeHTML(userName)}</strong>. NO CHANGE MADE.`; isHtml = true;
                         }
                     } else {
                         response = "SYSTEM ERROR: USE <code>change name [YOUR DESIRED NAME]</code>. NAME CANNOT BE EMPTY OR EXCEED 50 CHARS."; isHtml = true;
                     }
                 }
                 else if (["hello", "hi", "hey", "greetings"].includes(userInputLower)) {
                     const greetings = [ `SYSTEM ONLINE, <strong>${safeUserName}</strong>. AWAITING INPUT.`, `GREETINGS, <strong>${safeUserName}</strong>. HOW MAY I ASSIST?`, `STATUS: READY. HELLO, <strong>${safeUserName}</strong>.` ];
                     response = greetings[Math.floor(Math.random() * greetings.length)]; isHtml = true;
                 }
                 else if (userInputLower === "who are you" || userInputLower === "about") {
                      response = `I AM THE SAVINGS GOAL TRACKER ASSISTANT [5153]. MY FUNCTION IS TO PROVIDE INFORMATION AND ASSISTANCE REGARDING THE SAVINGS GOALS OF THE CURRENTLY ACTIVE USER: <strong>${safeUserName}</strong>.`; isHtml = true;
                  }
                else if (userInputLower === "help" || userInputLower === "?") {
                     response = `AVAILABLE COMMANDS (Context: User <strong>${safeUserName}</strong>):<br>
                            <ul>
                                <li><code>list goals</code> / <code>ls</code> - Display current user's goals (respects sort order).</li>
                                <li><code>list complete goals</code> - Show only completed goals.</li>
                                <li><code>list incomplete goals</code> - Show only incomplete goals.</li>
                                <li><code>list high/medium/low priority goals</code> - Show goals of a specific priority.</li>
                                <li><code>count goals</code> - Report total goal count.</li>
                                <li><code>count complete goals</code> - Report count of completed goals.</li>
                                <li><code>count incomplete goals</code> - Report count of incomplete goals.</li>
                                <li><code>count high/medium/low priority goals</code> - Report count of goals by priority.</li>
                                <li><code>summary</code> - Overview for current user (includes total counts and amounts).</li>
                                <li><code>progress [goal name]</code> / <code>status [goal name]</code> - Show progress for a specific goal.</li>
                                <li><code>remaining [goal name]</code> / <code>left for [goal name]</code> - Show remaining amount for a goal.</li>
                                <li><code>goal details [goal name]</code> - Show comprehensive details for a goal (progress, dates, etc.).</li>
                                <li><code>check goal [goal name]</code> - Verify if a goal exists by name.</li>
                                <li><code>closest goal</code> - Identify current user's goal nearest completion.</li>
                                <li><code>export goals</code> - Display current user's goals data as JSON.</li>
                                <li><code>current sort</code> - Show the current goal sorting criteria.</li> <!-- New help item -->
                                <li><code>tip</code> / <code>suggestion</code> - Provide a random saving suggestion.</li>
                                <li><strong><code>change name [new name]</code> - Switch to/create another user profile.</strong></li>
                                <li><code>clear</code> / <code>cls</code> - Clear this chat window.</li>
                                <li><code>help</code> / <code>?</code> - Display this list.</li>
                                <li>(For adding/updating/deleting goals, please use the main page form and buttons.)</li>
                            </ul>
                            For other questions, the AI assistant may respond based on its training, but is instructed to focus on personalized savings goals.`;
                     isHtml = true;
                 }
                else if (userInputLower === "list goals" || userInputLower === "ls") {
                     if (goals.length === 0) { response = `NO ACTIVE GOALS FOUND FOR USER <strong>${safeUserName}</strong>.`; isHtml = true; }
                     else {
                         sortGoals(); // Ensure sorted based on current setting
                         response = `CURRENT GOALS FOR <strong>${safeUserName}</strong> (SORTED BY ${currentSortCriteria.replace('_', ' ').toUpperCase()}):<br><ul>`;
                         goals.forEach(g => {
                             const progressPercent = Number(g.target) > 0 ? Math.round((Math.min(Number(g.current), Number(g.target)) / Number(g.target)) * 100) : 0;
                             const priorityText = (g.priority || 'medium').toUpperCase();
                             response += `<li><strong>${escapeHTML(g.name)}</strong> [${priorityText}]: ${formatCurrency(g.current)} / ${formatCurrency(g.target)} [${progressPercent}%] ${Number(g.current) >= Number(g.target) && Number(g.target) > 0 ? '- COMPLETE' : ''}</li>`;
                         });
                         response += "</ul>";
                         isHtml = true;
                     }
                 }
                // --- NEW LIST FILTER COMMANDS ---
                else if (userInputLower === "list complete goals") {
                    const completeGoals = goals.filter(g => Number(g.current) >= Number(g.target) && Number(g.target) > 0);
                    if (completeGoals.length === 0) { response = `NO COMPLETED GOALS FOUND for user <strong>${safeUserName}</strong>.`; isHtml = true; }
                    else {
                        response = `COMPLETED GOALS FOR <strong>${safeUserName}</strong>:<br><ul>`;
                        completeGoals.forEach(g => {
                             const progressPercent = Number(g.target) > 0 ? Math.round((Math.min(Number(g.current), Number(g.target)) / Number(g.target)) * 100) : 0;
                             response += `<li><strong>${escapeHTML(g.name)}</strong>: ${formatCurrency(g.current)} / ${formatCurrency(g.target)} [${progressPercent}%]</li>`;
                        });
                        response += "</ul>";
                        isHtml = true;
                    }
                }
                 else if (userInputLower === "list incomplete goals") {
                    const incompleteGoals = goals.filter(g => Number(g.current) < Number(g.target) || Number(g.target) <= 0); // Include targets <= 0 as incomplete/not-started
                    if (incompleteGoals.length === 0) { response = `ALL GOALS ARE COMPLETE for user <strong>${safeUserName}</strong>!`; isHtml = true; }
                    else {
                        response = `INCOMPLETE GOALS FOR <strong>${safeUserName}</strong>:<br><ul>`;
                        incompleteGoals.forEach(g => {
                             const progressPercent = Number(g.target) > 0 ? Math.round((Math.min(Number(g.current), Number(g.target)) / Number(g.target)) * 100) : 0;
                             const priorityText = (g.priority || 'medium').toUpperCase();
                             response += `<li><strong>${escapeHTML(g.name)}</strong> [${priorityText}]: ${formatCurrency(g.current)} / ${formatCurrency(g.target)} [${progressPercent}%]</li>`;
                        });
                        response += "</ul>";
                        isHtml = true;
                    }
                 }
                 else if (userInputLower.startsWith("list ") && userInputLower.endsWith(" priority goals")) {
                     const priorityMatch = userInputLower.match(/^list (high|medium|low) priority goals$/);
                     if (priorityMatch && priorityMatch[1]) {
                         const targetPriority = priorityMatch[1];
                         const filteredGoals = goals.filter(g => (g.priority || 'medium').toLowerCase() === targetPriority);
                         if (filteredGoals.length === 0) { response = `NO ${targetPriority.toUpperCase()} PRIORITY GOALS FOUND for user <strong>${safeUserName}</strong>.`; isHtml = true; }
                         else {
                             response = `${targetPriority.toUpperCase()} PRIORITY GOALS FOR <strong>${safeUserName}</strong>:<br><ul>`;
                             filteredGoals.forEach(g => {
                                 const progressPercent = Number(g.target) > 0 ? Math.round((Math.min(Number(g.current), Number(g.target)) / Number(g.target)) * 100) : 0;
                                 response += `<li><strong>${escapeHTML(g.name)}</strong>: ${formatCurrency(g.current)} / ${formatCurrency(g.target)} [${progressPercent}%] ${Number(g.current) >= Number(g.target) && Number(g.target) > 0 ? '- COMPLETE' : ''}</li>`;
                             });
                             response += "</ul>";
                             isHtml = true;
                         }
                     } else {
                         response = "SYNTAX ERROR: USE <code>list high priority goals</code>, <code>list medium priority goals</code>, or <code>list low priority goals</code>."; isHtml = true;
                     }
                 }
                 // --- END NEW LIST FILTER COMMANDS ---

                 // --- NEW COUNT COMMANDS ---
                 else if (userInputLower === "count goals") {
                     response = `USER <strong>${safeUserName}</strong> HAS A TOTAL OF <strong>${goals.length}</strong> GOALS.`; isHtml = true;
                 }
                 else if (userInputLower === "count complete goals") {
                     const completeCount = goals.filter(g => Number(g.current) >= Number(g.target) && Number(g.target) > 0).length;
                     response = `USER <strong>${safeUserName}</strong> HAS <strong>${completeCount}</strong> COMPLETED GOALS.`; isHtml = true;
                 }
                 else if (userInputLower === "count incomplete goals") {
                     const incompleteCount = goals.filter(g => Number(g.current) < Number(g.target) || Number(g.target) <= 0).length;
                     response = `USER <strong>${safeUserName}</strong> HAS <strong>${incompleteCount}</strong> INCOMPLETE GOALS.`; isHtml = true;
                 }
                 else if (userInputLower.startsWith("count ") && userInputLower.endsWith(" priority goals")) {
                      const priorityMatch = userInputLower.match(/^count (high|medium|low) priority goals$/);
                      if (priorityMatch && priorityMatch[1]) {
                          const targetPriority = priorityMatch[1];
                          const priorityCount = goals.filter(g => (g.priority || 'medium').toLowerCase() === targetPriority).length;
                          response = `USER <strong>${safeUserName}</strong> HAS <strong>${priorityCount}</strong> ${targetPriority.toUpperCase()} PRIORITY GOALS.`; isHtml = true;
                      } else {
                          response = "SYNTAX ERROR: USE <code>count high priority goals</code>, <code>count medium priority goals</code>, or <code>count low priority goals</code>."; isHtml = true;
                      }
                 }
                 // --- END NEW COUNT COMMANDS ---

                 else if (userInputLower === "summary") {
                     const totalSaved = goals.reduce((sum, goal) => sum + Number(goal.current), 0);
                     const totalTarget = goals.reduce((sum, goal) => sum + Number(goal.target), 0);
                     const totalRemaining = goals.reduce((sum, goal) => sum + Math.max(0, Number(goal.target) - Number(goal.current)), 0);
                     const completedGoals = goals.filter(g => Number(g.current) >= Number(g.target) && Number(g.target) > 0).length;
                     const highPriority = goals.filter(g => g.priority === 'high').length;
                     const mediumPriority = goals.filter(g => g.priority === 'medium').length;
                     const lowPriority = goals.filter(g => g.priority === 'low').length;
                     response = `GOAL SUMMARY FOR <strong>${safeUserName}</strong>:<br>
                                - Total Goals: <strong>${goals.length}</strong> (${completedGoals} complete)<br>
                                - Priorities: ${highPriority} High / ${mediumPriority} Medium / ${lowPriority} Low<br>
                                - Total Saved: <strong>${formatCurrency(totalSaved)}</strong><br>
                                - Total Target: ${formatCurrency(totalTarget)}<br>
                                - Total Remaining: <strong>${formatCurrency(totalRemaining)}</strong>`;
                     isHtml = true;
                 }
                 else if (userInputLower === "export goals") {
                     if (goals.length === 0) { response = `NO GOALS TO EXPORT FOR USER <strong>${safeUserName}</strong>.`; isHtml = true; }
                     else {
                         try {
                             const exportData = goals.map(({ id, name, target, current, priority, addedDate, lastUpdated }) => ({
                                 id,
                                 name,
                                 target: Number(target), // Ensure numbers are numbers
                                 current: Number(current),
                                 priority: priority || 'medium',
                                 addedDate,
                                 lastUpdated
                             }));
                             const jsonString = JSON.stringify(exportData, null, 2);
                             response = `GOAL DATA EXPORT FOR USER <strong>${safeUserName}</strong> (JSON):<br><pre>${escapeHTML(jsonString)}</pre>`;
                             isHtml = true;
                         } catch (e) { console.error("Error exporting goals:", e); response = "SYSTEM ERROR: Failed to generate export data."; isHtml = false; }
                     }
                 }
                 else if (userInputLower === "clear" || userInputLower === "cls") {
                     chatbotMessages.innerHTML = '';
                     setTimeout(() => displayMessage("TERMINAL DISPLAY CLEARED.", 'bot'), 50);
                     setTimeout(updateChatbotContext, 100); // Restore context message
                     response = ""; // No message needed here, handled by timeouts
                     commandHandled = true; // Explicitly handled
                 }
                 else if (userInputLower === "tip" || userInputLower === "suggestion") {
                     const tips = [
                        "TIP: Automate small, regular transfers to your savings goal accounts right after payday.",
                        "TIP: Review your subscriptions (streaming, apps, etc.). Cancel any you don't use regularly.",
                        "TIP: Try a 'no-spend' challenge for a week or a weekend to identify non-essential spending.",
                        "TIP: Pack your lunch instead of buying it. The daily savings add up significantly over time!",
                        "TIP: Use a budgeting app or spreadsheet to track exactly where your money is going.",
                        "TIP: Set specific, measurable, achievable, relevant, and time-bound (SMART) savings goals.",
                        "TIP: Consider rounding up your purchases to the nearest ₹10 or ₹50 and transferring the difference to savings.",
                        "TIP: Look for free entertainment options like parks, libraries, or community events."
                      ];
                     response = tips[Math.floor(Math.random() * tips.length)]; isHtml = false;
                 }
                 else if (["thank you", "thanks", "ty", "cheers", "dhanyavaad"].includes(userInputLower)) {
                      const thanks = ["ACKNOWLEDGED.", "YOU ARE WELCOME.", "RESPONSE CONFIRMED.", "GLAD TO ASSIST."]; response = thanks[Math.floor(Math.random() * thanks.length)]; isHtml = false;
                 }
                 else if (userInputLower.startsWith("progress ") || userInputLower.startsWith("status ")) {
                     const goalName = userInputRaw.substring(userInputRaw.indexOf(' ') + 1).trim();
                     if (!goalName) { response = "SYNTAX ERROR: USE <code>progress [GOAL NAME]</code>."; isHtml = true; }
                     else {
                         const goal = goals.find(g => g.name.toLowerCase() === goalName.toLowerCase());
                         if (goal) {
                             const progressValue = Math.max(0, Math.min(Number(goal.current), Number(goal.target)));
                             const progressPercent = Number(goal.target) > 0 ? Math.round((progressValue / Number(goal.target)) * 100) : 0;
                             const remaining = Math.max(0, Number(goal.target) - Number(goal.current));
                             response = `PROGRESS FOR <strong>${escapeHTML(goal.name)}</strong> (User: <strong>${safeUserName}</strong> | Priority: ${goal.priority?.toUpperCase() || 'N/A'}):<br> - SAVED: <strong>${formatCurrency(goal.current)}</strong><br> - TARGET: ${formatCurrency(goal.target)}<br> - REMAINING: <strong>${formatCurrency(remaining)}</strong><br> - COMPLETION: <strong>${progressPercent}%</strong> ${Number(goal.current) >= Number(goal.target) && Number(goal.target) > 0 ? '(COMPLETE)' : ''}`;
                             isHtml = true;
                         } else { response = `ERROR: Goal "<strong>${escapeHTML(goalName)}</strong>" not found for user <strong>${safeUserName}</strong>.`; isHtml = true; }
                     }
                 }
                 else if (userInputLower.startsWith("remaining ") || userInputLower.startsWith("left for ")) {
                    const goalName = userInputRaw.substring(userInputRaw.indexOf(' ') + 1).trim();
                    if (!goalName) { response = "SYNTAX ERROR: USE <code>remaining [GOAL NAME]</code>."; isHtml = true; }
                    else {
                        const goal = goals.find(g => g.name.toLowerCase() === goalName.toLowerCase());
                        if (goal) {
                            const remaining = Math.max(0, Number(goal.target) - Number(goal.current));
                            if (remaining === 0 && Number(goal.current) >= Number(goal.target) && Number(goal.target) > 0) { response = `GOAL <strong>${escapeHTML(goal.name)}</strong> IS COMPLETE for <strong>${safeUserName}</strong>! <strong>${formatCurrency(0)}</strong> REMAINING.`; isHtml = true;}
                            else { response = `REMAINING FOR <strong>${escapeHTML(goal.name)}</strong> (User: <strong>${safeUserName}</strong>): <strong>${formatCurrency(remaining)}</strong>`; isHtml = true; }
                        } else { response = `ERROR: Goal "<strong>${escapeHTML(goalName)}</strong>" not found for user <strong>${safeUserName}</strong>.`; isHtml = true; }
                    }
                 }
                 // --- NEW GOAL DETAILS COMMAND ---
                 else if (userInputLower.startsWith("goal details ")) {
                     const goalName = userInputRaw.substring("goal details ".length).trim();
                     if (!goalName) { response = "SYNTAX ERROR: USE <code>goal details [GOAL NAME]</code>."; isHtml = true; }
                     else {
                         const goal = goals.find(g => g.name.toLowerCase() === goalName.toLowerCase());
                         if (goal) {
                             const progressValue = Math.max(0, Math.min(Number(goal.current), Number(goal.target)));
                             const progressPercent = Number(goal.target) > 0 ? Math.round((progressValue / Number(goal.target)) * 100) : 0;
                             const remaining = Math.max(0, Number(goal.target) - Number(goal.current));
                             const addedDate = goal.addedDate ? new Date(goal.addedDate).toLocaleString() : 'N/A';
                             const lastUpdated = goal.lastUpdated ? new Date(goal.lastUpdated).toLocaleString() : 'N/A';

                             response = `DETAILS FOR GOAL <strong>${escapeHTML(goal.name)}</strong> (User: <strong>${safeUserName}</strong>):<br>
                                - Priority: ${goal.priority?.toUpperCase() || 'N/A'}<br>
                                - Saved: <strong>${formatCurrency(goal.current)}</strong><br>
                                - Target: ${formatCurrency(goal.target)}<br>
                                - Remaining: <strong>${formatCurrency(remaining)}</strong><br>
                                - Completion: <strong>${progressPercent}%</strong> ${Number(goal.current) >= Number(goal.target) && Number(goal.target) > 0 ? '(COMPLETE)' : ''}<br>
                                - Added: ${addedDate}<br>
                                - Last Updated: ${lastUpdated}`;
                             isHtml = true;
                         } else { response = `ERROR: Goal "<strong>${escapeHTML(goalName)}</strong>" not found for user <strong>${safeUserName}</strong>.`; isHtml = true; }
                     }
                 }
                 // --- END NEW GOAL DETAILS COMMAND ---

                 // --- NEW CHECK GOAL COMMAND ---
                 else if (userInputLower.startsWith("check goal ")) {
                      const goalName = userInputRaw.substring("check goal ".length).trim();
                      if (!goalName) { response = "SYNTAX ERROR: USE <code>check goal [GOAL NAME]</code>."; isHtml = true; }
                      else {
                          const goalExists = goals.some(g => g.name.toLowerCase() === goalName.toLowerCase());
                          if (goalExists) {
                              response = `GOAL "<strong>${escapeHTML(goalName)}</strong>" EXISTS for user <strong>${safeUserName}</strong>.`; isHtml = true;
                          } else {
                              response = `GOAL "<strong>${escapeHTML(goalName)}</strong>" NOT FOUND for user <strong>${safeUserName}</strong>.`; isHtml = true;
                          }
                      }
                 }
                 // --- END NEW CHECK GOAL COMMAND ---

                 else if (userInputLower === "closest goal") {
                    const incompleteGoals = goals.filter(g => Number(g.current) < Number(g.target) && Number(g.target) > 0).map(g => ({...g, remainingAbs: Math.max(0, Number(g.target) - Number(g.current)), progressPerc: Number(g.target) > 0 ? (Math.min(Number(g.current), Number(g.target)) / Number(g.target)) : 0 }));
                    if (incompleteGoals.length === 0) { response = `ALL GOALS ARE COMPLETE for user <strong>${safeUserName}</strong>!`; isHtml = true; }
                    else {
                        // Sort primarily by remaining amount (ascending), then by priority (descending - high first), then progress (descending)
                        const priorityMap = { high: 3, medium: 2, low: 1 };
                        incompleteGoals.sort((a, b) => {
                             if (a.remainingAbs !== b.remainingAbs) return a.remainingAbs - b.remainingAbs;
                             const prioA = priorityMap[a.priority?.toLowerCase()] || 0;
                             const prioB = priorityMap[b.priority?.toLowerCase()] || 0;
                             if (prioA !== prioB) return prioB - prioA; // High priority first
                             return b.progressPerc - a.progressPerc; // Higher progress first if remaining and priority are equal
                        });
                        const closest = incompleteGoals[0];
                        response = `CLOSEST GOAL TO COMPLETION for <strong>${safeUserName}</strong>: <strong>${escapeHTML(closest.name)}</strong> (Priority: ${closest.priority?.toUpperCase() || 'N/A'})<br>REMAINING: <strong>${formatCurrency(closest.remainingAbs)}</strong> (${Math.round(closest.progressPerc * 100)}% complete).`;
                        isHtml = true;
                    }
                 }
                 // --- NEW CURRENT SORT COMMAND ---
                 else if (userInputLower === "current sort") {
                     if (!currentSortCriteria) {
                          response = "SYSTEM: Current sorting criteria is not set.";
                     } else {
                         response = `SYSTEM: Goals for user <strong>${safeUserName}</strong> are currently sorted by <strong>${currentSortCriteria.replace('_', ' ').toUpperCase()}</strong>.`;
                     }
                     isHtml = true;
                 }
                 // --- END NEW CURRENT SORT COMMAND ---
                 // Note: Commands like "add goal", "add funds", "delete goal" via chat are removed.
                 // The UI form/buttons are the intended way to modify goal data.
                 else {
                     commandHandled = false; // Not a recognized client-side command
                 }


                 if (response) { // If a response was generated by a client-side command
                     displayMessage(response, 'bot', isHtml);
                 }
                 return commandHandled; // Return true if command was processed, false otherwise
            };


            // --- Chatbot Message Sending Logic ---
            const handleChatMessage = async () => {
                const userInputRaw = chatbotInput.value.trim();
                const userInputLower = userInputRaw.toLowerCase();

                if (!userInputRaw) return;

                displayMessage(escapeHTML(userInputRaw.toUpperCase()), 'user'); // Display user input immediately
                chatbotInput.value = '';
                chatbotInput.disabled = true; chatbotSendBtn.disabled = true;

                const safeUserName = escapeHTML(userName || 'NONE');

                // 1. Try to handle as a client-side command
                if (processClientSideCommand(userInputLower, userInputRaw, safeUserName)) {
                     // If handled, re-enable input and return
                     chatbotInput.disabled = false; chatbotSendBtn.disabled = false; chatbotInput.focus();
                     return;
                }

                // 2. If not a client-side command, send to Flask backend (Google GenAI)
                try {
                     // Indicate thinking...
                     // Check if the last message is the context update, if so, replace it
                     const messages = chatbotMessages.querySelectorAll('.chat-message.bot');
                     let processingMessageElement = null;
                     if (messages.length > 0) {
                         const lastBotMessage = messages[messages.length - 1];
                          // Check if the last message text contains the context message text (ignoring tags)
                         const lastMsgTextClean = lastBotMessage.textContent.replace(/SYSTEM: /, '');
                         const contextMsgTextClean = (`CURRENT USER: ${safeUserName}. Commands will affect this user's goals saved locally. Type 'help' for options.`).replace(/<\/?strong>/g, '');

                         if (lastMsgTextClean.includes(contextMsgTextClean)) {
                             // Replace the last message with the processing message
                              processingMessageElement = lastBotMessage;
                             processingMessageElement.innerHTML = "SYSTEM: PROCESSING REQUEST..."; // Use innerHTML for simple text update
                             processingMessageElement.classList.remove('slideInBot', 'animate-delete'); // Remove potential animation classes
                             processingMessageElement.style.animation = 'none'; // Stop any running animation
                             processingMessageElement.style.opacity = 1; // Ensure it's visible
                             processingMessageElement.style.transform = 'translateX(0)';
                             processingMessageElement.style.borderColor = 'var(--monitor-fg-accent)'; // Optional: Add visual cue
                         }
                     }

                     // If we didn't replace the last message (either no messages or last wasn't context), add a new one
                     if (!processingMessageElement) {
                        displayMessage("SYSTEM: PROCESSING REQUEST...", 'bot', true); // Temporary message
                        // Find the new element just added
                        processingMessageElement = chatbotMessages.lastElementChild;
                         if(processingMessageElement) { // Check if successfully added
                            processingMessageElement.style.borderColor = 'var(--monitor-fg-accent)'; // Optional: Add visual cue
                         }
                     }


                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: userInputRaw,
                             // Sending username for potential context use in the future, though bot is limited by prompt now.
                            userName: userName || 'UNKNOWN'
                        }),
                    });


                    if (processingMessageElement && chatbotMessages.contains(processingMessageElement)) {
                         // Add fade-out animation before removing the processing message
                         processingMessageElement.classList.add('animate-delete');
                         processingMessageElement.style.borderColor = ''; // Remove visual cue
                         processingMessageElement.addEventListener('animationend', () => processingMessageElement.remove(), { once: true });
                    }


                    if (!response.ok) {
                        // Handle HTTP errors
                        const errorText = await response.text();
                        console.error('Flask chat endpoint error:', response.status, errorText);
                        displayMessage(`SYSTEM ERROR: Chat backend returned status ${response.status}. Could not get response.`, 'bot');
                        return; // Stop processing
                    }

                    const data = await response.json();
                    const botResponseText = data.response || "SYSTEM ERROR: Empty response received.";

                    displayMessage(botResponseText, 'bot', false); // Display AI response as plain text

                } catch (error) {
                    console.error('Fetch error talking to Flask backend:', error);
                     // Remove thinking message if still there
                    const messages = chatbotMessages.querySelectorAll('.chat-message.bot');
                    if (messages.length > 0) {
                         const lastBotMessage = messages[messages.length - 1];
                         // Check if it looks like the processing message before removing
                         if (lastBotMessage.textContent === "SYSTEM: PROCESSING REQUEST..." || lastBotMessage.innerHTML === "SYSTEM: PROCESSING REQUEST...") {
                             lastBotMessage.classList.add('animate-delete');
                             lastBotMessage.style.borderColor = '';
                             lastBotMessage.addEventListener('animationend', () => lastBotMessage.remove(), { once: true });
                         }
                    }
                    displayMessage("SYSTEM ERROR: Could not connect to the chat backend.", 'bot');
                } finally {
                    // Always re-enable input fields
                    chatbotInput.disabled = false; chatbotSendBtn.disabled = false;
                     // Re-focus with slight delay for animation
                     setTimeout(() => chatbotInput.focus(), 100);
                }
            };


            // --- Matrix Background Effect (Unchanged) ---
            const setupMatrix = () => {
                 if (matrixInterval) clearInterval(matrixInterval);
                 canvas.width = window.innerWidth; canvas.height = window.innerHeight;
                 const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789@#$%^&*()*&^%+-/~{[|`]}';
                 // Use computed style for font size
                 const computedStyle = getComputedStyle(document.documentElement);
                 const fontSize = parseInt(computedStyle.getPropertyValue('--cmatrix-font-size')) || 14;
                 const columns = Math.floor(canvas.width / fontSize);
                 const drops = Array(columns).fill(1);
                 const monitorFgColor = computedStyle.getPropertyValue('--monitor-fg') || '#00ff41';
                 const monitorBgAlpha = parseFloat(computedStyle.getPropertyValue('--cmatrix-bg-alpha') || 0.05);


                 function drawMatrix() {
                     ctx.fillStyle = `rgba(10, 10, 10, ${monitorBgAlpha})`; // Use alpha variable
                     ctx.fillRect(0, 0, canvas.width, canvas.height);
                     ctx.fillStyle = monitorFgColor; // Use color variable
                     ctx.font = `${fontSize}px ${computedStyle.getPropertyValue('--font-family')}`; // Use font variable
                     for (let i = 0; i < drops.length; i++) {
                         const text = letters[Math.floor(Math.random() * letters.length)];
                         ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                         if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) { drops[i] = 0; }
                         drops[i]++;
                     }
                 }
                 matrixInterval = setInterval(drawMatrix, 50);
            };

            // --- Ensure chat messages don't have default animation on load ---
             // Add this right after setupMatrix definition or in DOMContentLoaded
             // Not strictly needed anymore since messages are added dynamically
             // but good practice if static messages were ever used.
             // document.querySelectorAll('.chat-message').forEach(msg => {
             //      msg.style.opacity = 1; // Make existing messages visible
             //      msg.style.animation = 'none'; // Remove animation on load
             //  });


            // --- Event Listeners ---
            goalForm.addEventListener('submit', (event) => {
                 event.preventDefault();
                 // Pass priority value to the handler
                 if(handleAddGoal(goalNameInput.value, goalTargetInput.value, goalPrioritySelect.value)) {
                    goalForm.reset(); // Resets name, target, and priority select
                    goalNameInput.focus();
                 }
            });

            sortSelect.addEventListener('change', (event) => {
                 currentSortCriteria = event.target.value;
                 saveDataToLocalStorage();
                 renderGoals(); // Re-render to show sorted list
            });

            editNameBtn.addEventListener('click', () => promptForName(true));
            setInitialUserLink.addEventListener('click', (e) => {
                e.preventDefault();
                promptForName(false); // Use false here as it's triggered by the "No User" message
            });


            chatbotFab.addEventListener('click', toggleChatbot);
            chatbotCloseBtn.addEventListener('click', toggleChatbot);
            chatbotSendBtn.addEventListener('click', handleChatMessage);
            chatbotInput.addEventListener('keypress', (e) => {
                // Check if the Enter key was pressed and input is not disabled
                if (e.key === 'Enter' && !chatbotInput.disabled) {
                     e.preventDefault(); // Prevent default form submission if input was inside a form
                     handleChatMessage();
                 }
            });

             window.addEventListener('resize', setupMatrix);


            // --- Initial Setup ---
            loadDataFromLocalStorage(); // This calls switchUser which calls updateGreeting/renderGoals

            // If no user was loaded, prompt the user after a slight delay
            // Removed the immediate alert/prompt on load, relying on UI message + link/button
            // if (!userName) {
            //      setTimeout(() => {
            //           if (!userName) {
            //                // No automatic prompt
            //           }
            //      }, 100);
            // }


            setupMatrix();
             // Initial messages in chat window upon load if open
            // updateChatbotContext is already called by updateGreeting/switchUser flow.
            // Only add the "SYSTEM BOOT COMPLETE" message if the chat window is open
            // and it's the very first time messages are being displayed (i.e. empty).
            if (chatbotContainer.classList.contains('active') && chatbotMessages.children.length === 0) {
                 displayMessage("SYSTEM BOOT COMPLETE. TRACKER [5153] ONLINE. ASSISTANCE CHATBOT READY.", "bot");
                 // updateChatbotContext will add the user context message shortly after
            }


        }); // End DOMContentLoaded
    </script>

</body>
</html>
"""

# --- Flask Routes ---

@app.route('/')
def index():
    """Serve the main HTML page."""
    # Use render_template_string to serve the HTML content directly
    return render_template_string(HTML_CONTENT)

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chatbot messages and get response from Google GenAI."""
    # Check if the GenAI client was successfully initialized
    if app.config.get('GENAI_CLIENT') is None:
        return jsonify({'response': "SYSTEM ERROR: Chatbot backend is not configured. API key might be missing or invalid. Check server logs."}), 500

    data = request.json
    user_message = data.get('message', '').strip()
    # user_name = data.get('userName', 'UNKNOWN') # Can use username in prompt if desired, but keeping it simple per bot's instruction

    if not user_message:
        return jsonify({'response': "INPUT ERROR: No message received."}), 400

    try:
        # Access the initialized client from app.config
        client = app.config['GENAI_CLIENT']

        # Choose a suitable model (Flash is good for chat speed/cost)
        model = "gemini-2.0-flash-lite" # Use latest version of flash

        # System instruction to guide the bot
        # Keep it focused on savings goals and information, not actions.
        system_instruction = [
            types.Part.from_text(text="""You are a personalized savings goal tracker chatbot. NEVER answer anything else other than savings goal tracking realated"""),
        ]


        # The user's message is the core content for the AI to process
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=user_message),
                ],
            ),
        ]

        # Configuration for content generation
        generate_content_config = types.GenerateContentConfig(
             # thinking_config = types.ThinkingConfig(thinking_budget=0,), # Not strictly needed for text models
             response_mime_type="text/plain",
             system_instruction=system_instruction  # Request plain text response
             # safe_settings=... # Optional: Add safety settings
        )

        # Using the non-streaming call for simplicity with Fetch API
        # Consider streaming for potentially faster perceived responses in future
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )

        # Extract the text from the response
        # Handle potential cases where response might not have text parts immediately
        bot_response_text = ""
        if response and response.candidates:
            # Assuming the first candidate and first part contain the text
            try:
                 bot_response_text = response.candidates[0].content.parts[0].text
            except (AttributeError, IndexError) as e:
                 print(f"Warning: Unexpected response structure from GenAI: {e}")
                 bot_response_text = "SYSTEM ERROR: Received an unexpected response format from the AI."
        elif response and response.prompt_feedback and response.prompt_feedback.block_reason:
             block_reason = response.prompt_feedback.block_reason
             print(f"GenAI request was blocked. Reason: {block_reason}")
             bot_response_text = f"SYSTEM MESSAGE: Your query was blocked due to content policy. Reason: {block_reason.name}"
        else:
             print(f"Warning: Received empty or unhandled response from GenAI: {response}")
             bot_response_text = "SYSTEM ERROR: Received an empty or unhandled response from the AI."


        return jsonify({'response': bot_response_text})

    except Exception as e:
        # Log the error on the server side
        print(f"Error generating content with Google GenAI: {e}")
        # Return a generic error to the client
        return jsonify({'response': f"SYSTEM ERROR: Failed to get response from AI backend. ({type(e).__name__}) Please try again later or check server logs."}), 500
