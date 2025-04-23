# Personalized Savings Goal Tracker Chatbot

A retro-themed, single-page web application for managing and tracking personal savings goals with multi-user support and an interactive chatbot interface, styled to resemble an old-school computer monitor.

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
*   💰 **Contribution Tracking:** Easily add funds to any specific goal.
*   🗑️ **Goal Deletion:** Remove goals you no longer need (requires confirmation via chatbot).
*   📊 **Dynamic Sorting:** Sort the goal list by various criteria:
    *   Date Added (Newest/Oldest)
    *   Priority (High-Low / Low-High)
    *   Name (A-Z / Z-A)
    *   Target Amount (Low-High / High-Low)
    *   Amount Remaining (Low-High / High-Low)
    *   Progress Percentage (High-Low / Low-High)
*   💾 **Local Persistence:** All user data and goal progress are saved in the browser's `localStorage`, allowing you to close the tab and resume later.
*   🤖 **Chatbot Assistant:**
    *   Interact with your goals using text commands (e.g., `add goal`, `list goals`, `add funds`, `delete goal`, `summary`).
    *   Switch users via command (`change name [username]`).
    *   Get help with available commands (`help`).
    *   Export goal data as JSON (`export goals`).
    *   Receive feedback and confirmation messages.
*   👾 **Retro Terminal UI:**
    *   Classic green-on-black monitor aesthetic.
    *   Animated CMatrix-style background effect.
    *   Scanline overlay for added vintage feel.
    *   Monospaced font throughout.
*   📱 **Responsive Design:** Adapts to different screen sizes (desktop, tablet, mobile).

## Running the Application 🏃‍♀️

This is a purely front-end application built with standard web technologies. No server or complex installation is required.

1.  **Download or Clone:**
    *   If you have Git:
        ```sh
        git clone <your-repository-url>
        cd <repository-directory>
        ```
    *   Alternatively, download the project files (HTML, CSS, JS) as a ZIP archive and extract them.

2.  **Open the HTML File:**
    *   Simply open the main HTML file (e.g., `index.html` or the name you gave it) in your preferred modern web browser (Chrome, Firefox, Edge, Safari recommended).

## Usage & Interaction 🛠️

1.  **Set User Identifier:** Upon first load (or if no user is active), you'll be prompted to enter a User Identifier (Name). This creates or loads your profile. All subsequent actions affect this active user.
2.  **Switch User:** Click the `[SWITCH]` button next to the user's name in the header or use the chatbot command `change name [new_username]` to switch between profiles.
3.  **Add a Goal:**
    *   Use the "> ADD NEW GOAL_" form.
    *   Enter a **Goal Name**.
    *   Enter the **Target Amount** (in ₹).
    *   Select a **Priority** (High/Medium/Low).
    *   Click "ADD GOAL".
    *   *Alternatively, use the chatbot:* `add goal [name] target [amount] priority [high/medium/low]`
4.  **View Goals:** Goals for the active user are displayed as cards under "> CURRENT GOALS_".
5.  **Interact with Goal Cards:**
    *   **View:** See Name, Target, Progress Bar, Percentage, Saved Amount, Remaining Amount, Priority, and Date Added.
    *   **Add Funds:** Enter an amount in the "ADD ₹" input field within the card and click "ADD FUNDS".
    *   **Delete:** Click the "DELETE" button (may require confirmation via chatbot command later if UI button is removed).
6.  **Sort Goals:** Use the "SORT BY:" dropdown menu above the goals list to reorder the cards.
7.  **Use the Chatbot:**
    *   Click the floating terminal icon (<i class="fa-solid fa-terminal"></i>) in the bottom-right corner to open the chat interface.
    *   Type commands into the input field (e.g., `list goals`, `summary`, `progress MyGoal`, `delete goal OldGoal`, `help`) and press Enter or click the send button (<i class="fa-solid fa-paper-plane"></i>).
    *   The chatbot provides feedback and performs actions for the *currently active user*.
    *   Click the '×' button or the terminal icon again to close the chat.
8.  **Data Persistence:** Your data is saved automatically to `localStorage` whenever you add/modify goals or switch users.

## Example Workflow 🚶‍♂️

1.  Open the HTML file. Prompt asks for User ID. Enter `ALOK`.
2.  Use the form to add a goal: Name="Gaming PC", Target="80000", Priority="High". Click "ADD GOAL".
3.  Use the form again: Name="Holiday Fund", Target="30000", Priority="Medium". Click "ADD GOAL".
4.  Find the "Gaming PC" card. Enter `5000` into its "ADD ₹" input field and click "ADD FUNDS". Observe the progress bar and amounts update.
5.  Click the chatbot FAB (<i class="fa-solid fa-terminal"></i>).
6.  Type `list goals` and press Enter. See both goals listed.
7.  Type `add funds 2500 to Holiday Fund` and press Enter. Observe the chatbot confirmation and the "Holiday Fund" card update in the main view.
8.  Type `summary` and press Enter to see overall progress for ALOK.
9.  Click the `[SWITCH]` button. Enter `PRIYA` when prompted. The goal list clears.
10. Add a goal for PRIYA using the form or chatbot.
11. Use the chatbot command `change name ALOK` to switch back. ALOK's goals reappear.
12. Close the browser tab and reopen the HTML file. ALOK's goals and progress should still be loaded.

## Technology Stack 💻

*   **HTML5:** Structure and content.
*   **CSS3:** Styling, layout (Flexbox, Grid), animations, retro theme (CSS Variables), scanlines effect.
*   **JavaScript (ES6+):** Core application logic, DOM manipulation, event handling, goal calculations, sorting, chatbot logic, `localStorage` interaction, Canvas API (for CMatrix background).
*   **Font Awesome:** Icons.

## Key Code Concepts ✨

*   **User-Specific Storage:** Uses a main object in `localStorage` keyed by `LOCAL_STORAGE_KEY`, containing `allUserData` (an object mapping usernames to their goal arrays) and `lastActiveUserName`.
*   **Dynamic Rendering:** JavaScript manipulates the DOM extensively to create, update, and remove goal cards based on the `goals` array for the active user.
*   **State Management:** Variables like `userName`, `goals`, `currentSortCriteria` hold the application's current state.
*   **Modular Functions:** Code is organized into functions for specific tasks (e.g., `handleAddGoal`, `renderGoals`, `saveDataToLocalStorage`, `switchUser`, `getBotResponse`).
*   **Event Delegation (Implicit):** Event listeners are added to dynamically created elements (buttons within goal cards).
*   **Chatbot Parser:** The `getBotResponse` function uses string matching and regular expressions (for commands like `add goal`, `add funds`) to understand user input.
*   **Canvas Animation:** The `setupMatrix` and `drawMatrix` functions create the animated background effect.

## Future Enhancements / Todo 📝

*   📈 More visual statistics (e.g., charts showing progress over time).
*   💾 Explicit Import/Export feature (e.g., download/upload JSON file).
*   🎨 Theme customization options (e.g., different monitor colors).
*   💡 Add deadline/target dates for goals.
*   🔔 Optional reminders or notifications.
*   🌐 More robust error handling and user feedback.
*   🧪 Unit/Integration tests.

## Contribution 🤝

Feel free to fork this repository, submit issues, or propose pull requests with improvements or new features!

## License 📜

MIT License
