**Verification Table**

| Item | PASS/FAIL | Evidence (code line / snippet) |
|------|-----------|--------------------------------|
| R1 – Log a drink (250 ml, 500 ml, custom) | PASS | `document.getElementById('b250').onclick=()=>handle(250);`  <br> `document.getElementById('b500').onclick=()=>handle(500);` <br> `document.getElementById('addCustom').onclick=()=>handle(document.getElementById('custom').value);` |
| R2 – Show today’s total, goal, percent, remaining | PASS | `function calc(st){ … const pct=Math.min((total/GOAL)*100,100); … }` <br> `document.getElementById('total').textContent=p.total;` etc. |
| R3 – Show streak of consecutive days goal met | PASS | `function dayChange(st){ if(st.todayDate!==todayISO()){ const newStreak=st.todayTotal>=GOAL?st.streak+1:0; … }}` <br> `document.getElementById('streak').textContent=state.streak;` |
| R4 – Reject nonsense input (0, negative, >2000) | PASS | `function isValid(v){ const n=Number(v); return Number.isFinite(n)&&n>0&&n<=2000; }` <br> `if(state.todayTotal===prev){showError('Enter 1‑2000 ml');}` |
| R5 – Reset today’s total | PASS | `document.getElementById('reset').onclick=()=>{state=resetToday(state);save(state);render();};` <br> `function resetToday(st){return{...st,todayTotal:0};}` |
| R6 – One‑page index.html with inline CSS & JS | PASS | Entire file is a single HTML document; CSS in `<style>` block; JS in `<script>` block. |
| R7 – No backend, no libraries, no build step | PASS | Only native browser APIs (`localStorage`, `document`, etc.) are used. |
| R8 – Persist data in `localStorage` | PASS | `function load(){const s=localStorage.getItem(KEY); …}` <br> `function save(s){localStorage.setItem(KEY,JSON.stringify(s));}` |
| R9 – Plain, readable, accessible design | PASS* | Semantic HTML (`<button>`, `<input>`), ARIA role on error: `<p id="error" role="alert"></p>`; colour contrast acceptable. |
| R10 – Core logic is pure & unit‑testable | PASS | Pure functions: `isValid`, `addDrink`, `resetToday`, `calc`, `dayChange` – no side effects, only return new state objects. |
| TC‑1 – Click 250 ml → total 250 ml, 12.5 %, remain 1750 ml | PASS | `handle(250)` → `addDrink` updates `todayTotal`; `calc` yields `pct=12.5`, `rem=1750`. |
| TC‑2 – Input –100 → validation fails, total unchanged, error shown | PASS | `isValid(-100)` returns false; `state.todayTotal===prev` triggers `showError('Enter 1‑2000 ml');`. |
| TC‑3 – Input 0 → validation fails, total unchanged, error shown | PASS | `isValid(0)` returns false; same error path as TC‑2. |
| TC‑4 – Input 2100 → validation fails, total unchanged, error shown | PASS | `isValid(2100)` returns false; same error path. |
| TC‑5 – Custom field 500 ml → total increases by 500 ml | PASS | `handle(document.getElementById('custom').value)` passes 500 to `addDrink`, `calc` updates display. |
| TC‑6 – Reset today → total 0, 0 %, remain 2000 ml, streak unchanged | PASS | `resetToday(state)` sets `todayTotal` to 0; `render` shows `pct=0`, `rem=2000`; `streak` left untouched. |

\*R9 is marked PASS because the UI uses semantic elements and an `role="alert"` for errors, meeting basic accessibility, although a minor issue exists (see bugs).

---

**Bugs / Issues Identified**

| # | Description | Location |
|---|-------------|----------|
| 1 | `aria-live` is incorrectly placed in the CSS rule (`#error{color:red;aria-live:polite}`); `aria-live` is an HTML attribute, not a CSS property. | `<style>` block, line with `aria-live:polite`. |
| 2 | Day‑change detection (`dayChange`) runs only once at page load. If the page stays open across midnight, the streak and date will not update until a reload. | `let state=dayChange(load());` – no periodic check or `setInterval`. |
| 3 | The generic error message (“Enter 1‑2000 ml”) does not differentiate the specific cause (zero, negative, or >2000). While functional, it reduces UX clarity. | `showError('Enter 1‑2000 ml');` in `handle`. |

---

**Verdict**  
Overall the implementation satisfies all listed requirements and passes every test case; only minor accessibility and midnight‑crossing timing issues are present.