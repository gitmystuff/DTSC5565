## Requirements
- **R1** – Log a drink in ml (quick buttons for 250 ml, 500 ml, plus a custom amount).  
- **R2** – Show today’s total, the 2 000 ml goal, percent complete and remaining amount.  
- **R3** – Show a streak of consecutive days the goal was met.  
- **R4** – Reject nonsense input (zero, negative, > 2 000 ml per entry).  
- **R5** – Let the user reset today’s total.  
- **R6** – One‑page `index.html` with inline CSS & JavaScript.  
- **R7** – No backend, no libraries, no build step.  
- **R8** – Persist all data in the browser’s `localStorage`.  
- **R9** – Plain, readable, accessible design.  
- **R10** – Core logic must be pure functions that can be unit‑tested separately from the UI.

---

## Pieces
| Piece | What it does |
|-------|--------------|
| **Data model** | An object stored in `localStorage` with keys: `todayDate` (ISO string), `todayTotal` (ml), `streak` (days). |
| **Persistence layer** | Small wrapper (`loadState`, `saveState`) that reads/writes the data model to `localStorage`. |
| **Logic** | <ul><li>`addDrink(amount)` – validates (R4) then increments `todayTotal`.</li><li>`resetToday()` – sets `todayTotal` = 0 (R5).</li><li>`calculateProgress()` – returns total, percent, remaining (R2).</li><li>`updateStreak()` – after each day‑change, checks if previous day met 2 000 ml and updates `streak` (R3).</li><li>`isValidAmount(value)` – pure validator for input rules (R4).</li></ul> |
| **Screen (UI)** | <ul><li>Buttons “250 ml”, “500 ml”, “Custom” + numeric input field.</li><li>Display area for total, goal, percent, remaining (R2).</li><li>Streak display (R3).</li><li>“Reset today” button (R5).</li></ul> All elements are semantic HTML with appropriate ARIA labels for accessibility (R9). |
| **Entry point** | Inline script that wires UI events to the pure logic functions, calls `loadState` on page load, and writes back with `saveState`. Keeps UI code separate from testable logic (R10). |

---

## Input rules
- **Type**: must be a numeric value (integer or decimal) entered via button or custom field.  
- **Range**: `0 < value ≤ 2000`.  
- **Rejected**: zero, negative numbers, values greater than 2 000, non‑numeric strings, empty input.  
- On rejection the UI shows an accessible error message and does **not** modify any stored totals.

---

## Test cases
| # | Input → Expected result |
|---|--------------------------|
| 1 | Click **250 ml** button → total = 250 ml, percent = 12.5 %, remaining = 1 750 ml, streak unchanged. |
| 2 | Enter **‑100** (or click a button that would send –100) → validation fails, total unchanged, error shown. |
| 3 | Enter **0** → rejected, total unchanged, error shown. |
| 4 | Enter **2100** → rejected (above 2000 ml), total unchanged, error shown. |
| 5 | Custom field **500** ml → total increased by 500 ml, percent and remaining updated accordingly. |
| 6 | After logging some drinks, click **Reset today** → todayTotal = 0 ml, percent = 0 %, remaining = 2 000 ml; streak reflects only previous days (if yesterday met goal, streak stays 1, otherwise resets). |

All requirements R1‑R10 appear in the pieces or test cases, and no extra features are introduced.