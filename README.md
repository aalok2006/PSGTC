# Personalized Savings Goal Tracker Chatbot

A retro-themed, single-page web application for managing and tracking personal savings goals with multi-user support and an interactive chatbot interface, styled to resemble an old-school computer monitor. The chatbot uses a Python Flask backend powered by Google GenAI.

## 🚀 Live Demo

[![Visit Website](https://img.shields.io/badge/Launch%20Website-Click%20Here-brightgreen?style=for-the-badge&logo=firefox-browser)](https://psgtc.onrender.com)

![image](https://github.com/user-attachments/assets/cffff4cd-a50f-4387-b4c6-a45a9da466f1)

## Features 🚀

*   👤 **Multi-User Support:** Create and switch between different user profiles. Goal data is saved separately for each user.
*   🎯 **Goal Management:**
    *   Add new savings goals with a Name, Target Amount (₹), and Priority (High/Medium/Low).
    *   View all goals displayed as individual cards.
    *   Track progress visually with a progress bar and percentage.
    *   See current amount saved and amount remaining for each goal.
    *   Mark goals as complete automatically when the target is reached.
*   💰 **Contribution Tracking:** Easily add funds to any specific goal directly via the goal card.
*   🗑️ **Goal Deletion:** Remove goals you no longer need (requires confirmation via a browser dialog).
*   📊 **Dynamic Sorting:** Sort the goal list by various criteria: Date Added, Priority, Name, Target Amount, Amount Remaining, and Progress Percentage.
*   💾 **Local Persistence:** All user data and goal progress are saved securely in the browser's `localStorage`, allowing you to close the tab and resume later.
*   🤖 **Interactive Chatbot:**
    *   A built-in chatbot assistant interface.
    *   Handles specific client-side commands for data retrieval (`list goals`, `summary`, `progress [name]`, `closest goal`, `export goals`, `change name [user]`, `help`, `clear`).
    *   For general savings-related questions *not* covered by client commands, the chatbot interacts with a Python Flask backend using Google GenAI to provide responses (Note: The AI is specifically instructed to stay on topic related to savings and goals).
*   👾 **Retro Terminal UI:**
    *   Classic green-on-black monitor aesthetic with monospace font.
    *   Animated background effect resembling CMatrix using Canvas.
    *   Subtle scanline overlay for vintage feel.
*   📱 **Responsive Design:** Adapts gracefully to different screen sizes (desktop, tablet, mobile).

## Running the Application 🏃‍♀️

This application consists of a front-end single-page web app and a small Python Flask backend required for the chatbot's AI capabilities.

1.  **Prerequisites:**
    *   Python 3.6+
    *   `pip` package installer
    *   A Google Cloud Project with the Generative AI API enabled (or access via a Gemini API key).
    *   A Google Gemini API Key.

2.  **Setup Backend:**
    *   Save the provided Python code as `app.py`.
    *   Install the required Python packages:
        ```sh
        pip install Flask google-genai
        ```
    *   Set your Google Gemini API Key as an environment variable named `GEMINI_API_KEY`.
        *   *On Linux/macOS (for current session):*
            ```sh
            export GEMINI_API_KEY='YOUR_API_KEY'
            ```
        *   *On Windows (Command Prompt):*
            ```cmd
            set GEMINI_API_KEY=YOUR_API_KEY
            ```
        *   *On Windows (PowerShell):*
            ```powershell
            $env:GEMINI_API_KEY='YOUR_API_KEY'
            ```
        *   *Using a `.env` file (recommended for development):* Install `pip install python-dotenv` and add `GEMINI_API_KEY=YOUR_API_KEY` to a file named `.env` in the same directory as `app.py`. Your code should ideally load this automatically (the provided code snippet doesn't explicitly show `python-dotenv` usage, so setting it in the environment is the most direct way for this specific code).

3.  **Run the Flask App:**
    *   Open your terminal or command prompt in the directory where you saved `app.py`.
    *   Run the application:
        ```sh
        python app.py
        ```
    *   The server should start, typically indicating it's running on `http://127.0.0.1:5000/`.

4.  **Access the Application:**
    *   Open your web browser and go to the address provided by the Flask server (e.g., `http://127.0.0.1:5000/`).

*Note: You can open the HTML content within the `app.py` file directly in a browser (`data:text/html;base64,...` or extracting it), but the chatbot's AI features will **not** work without the Flask backend running.*

## Usage & Interaction 🛠️

1.  **Set User Identifier:** When you first open the app or switch users, you'll be prompted to enter a User Identifier (Name). This name is used to isolate your savings data in `localStorage`. Enter a name and click OK. Your name will appear in the header.
2.  **Switch User:** Click the `[SWITCH]` button next to your name in the header, or use the chatbot command `change name [new_username]` to switch between existing profiles or create a new one.
3.  **Add a Goal:**
    *   Use the "> ADD NEW GOAL_" form.
    *   Enter a **Goal Name**, **Target Amount** (in ₹), and select a **Priority**.
    *   Click "ADD GOAL".
    *   The new goal will appear in the list below.
4.  **View Goals:** Goals for the active user are displayed as cards under "> CURRENT GOALS_".
5.  **Interact with Goal Cards:**
    *   Each card shows the goal details, progress bar, and amounts.
    *   **Add Funds:** Enter an amount in the "ADD ₹" input field within the card and click "ADD FUNDS". The goal's current amount, progress, and remaining amount will update instantly.
    *   **Delete:** Click the "DELETE" button to remove a goal (a browser confirmation dialog will appear).
6.  **Sort Goals:** Use the "SORT BY:" dropdown menu above the goals list to reorder the goal cards dynamically.
7.  **Use the Chatbot:**
    *   Click the floating terminal icon (<i class="fa-solid fa-terminal"></i>) in the bottom-right corner to open the chat interface.
    *   Type commands (like `list goals`, `summary`, `help`) into the input field and press Enter or click the send button (<i class="fa-solid fa-paper-plane"></i>).
    *   The chatbot will respond with information or execute client-side actions (like switching users).
    *   For queries it doesn't recognize as specific commands, it will ask the AI backend (requires the Flask app to be running).
    *   Click the '×' button or the terminal icon again to close the chat.
8.  **Data Persistence:** Your data for each user is automatically saved to your browser's `localStorage` whenever changes are made.

## Example Workflow 🚶‍♂️

1.  Navigate to the application URL (e.g., `http://127.0.0.1:5000/`).
2.  When prompted, enter `SAMIR` as the user identifier.
3.  Use the form to add a goal: Name="New Laptop", Target="75000", Priority="High". Click "ADD GOAL".
4.  Add another: Name="Emergency Fund", Target="50000", Priority="Medium". Click "ADD GOAL".
5.  Find the "New Laptop" card. Enter `10000` in the "ADD ₹" field and click "ADD FUNDS". See the progress update.
6.  Click the floating terminal icon to open the chatbot.
7.  Type `summary` and press Enter. The chatbot will show your total saved, target, remaining, etc., for SAMIR.
8.  Type `progress Emergency Fund` and press Enter to see details for that specific goal.
9.  Type `change name JAYA` and press Enter. The user switches, and the goal list becomes empty.
10. Add a goal for JAYA: Name="Vacation", Target="120000", Priority="High".
11. Click the `[SWITCH]` button. Enter `SAMIR` again. SAMIR's goals ("New Laptop", "Emergency Fund") reappear with their saved amounts.
12. Close the browser and reopen it. SAMIR's data should still be loaded.

## Technology Stack 💻

*   **Frontend:**
    *   **HTML5:** Structure
    *   **CSS3:** Styling, Retro Theme, Animations, Responsive Design, Canvas Scanlines.
    *   **JavaScript (ES6+):** Application Logic, DOM Manipulation, Event Handling, Local Storage Management, Goal Calculations, Sorting, Client-Side Chatbot Commands, Canvas Matrix Animation.
    *   **Font Awesome:** Icons.
*   **Backend (for AI Chatbot):**
    *   **Python:** Server-side language.
    *   **Flask:** Micro web framework.
    *   **Google GenAI Client:** For interacting with the Gemini API.

## Key Code Concepts ✨

*   **User-Specific Storage:** Data is stored in `localStorage` under a versioned key (`savingsTrackerData_IBM5153_v3_UserSpecific`). This object contains `allUserData` (mapping usernames to their goal arrays) and `lastActiveUserName` to remember the last used profile.
*   **Dynamic Rendering:** JavaScript generates and updates goal cards directly in the DOM based on the `goals` array for the active user.
*   **State Management:** Core application state (`userName`, `goals`, `allUserData`, `currentSortCriteria`) is held in JavaScript variables and persisted to `localStorage`.
*   **Modular Functions:** Logic is broken down into functions for clear handling of goals (`handleAddGoal`, `handleAddContribution`, `handleDeleteGoal`), UI updates (`renderGoals`, `updateGoalElement`, `updateGreeting`), user management (`switchUser`, `promptForName`), and chatbot interaction (`toggleChatbot`, `displayMessage`, `handleChatMessage`, `processClientSideCommand`).
*   **Chatbot Command Parsing:** Client-side commands (`processClientSideCommand`) use string matching to identify known commands and extract parameters before falling back to the backend for AI processing.
*   **Flask Endpoint (`/chat`):** Receives user messages, formats them for the Google GenAI API with a specific `system_instruction`, sends the request, and returns the AI's plain text response to the frontend.
*   **Canvas Animation:** A dedicated JavaScript function uses the Canvas API to draw and animate the matrix background effect.

## Future Enhancements / Todo 📝

*   📈 More advanced reporting and visual statistics (e.g., charts).
*   💾 Explicit JSON data Import/Export utility (download/upload files).
*   🎨 Theme customization options (e.g., different monitor colors, fonts).
*   📅 Add deadlines or target dates for goals.
*   🔔 Optional goal-based reminders or notifications.
*   🌐 More robust error handling and detailed user feedback.
*   🧪 Add automated unit/integration tests.
*   🤝 Improve chatbot's understanding of natural language goal additions/updates (requires more complex backend interaction and state management synchronization).

## Contribution 🤝

Feel free to fork this repository, submit issues, or propose pull requests with improvements or new features!

## Credits ✨

Created by: Aalok Kumar Yadav

## License 📜

MIT License
