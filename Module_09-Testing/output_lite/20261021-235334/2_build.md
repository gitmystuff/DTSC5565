```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Water Tracker</title>
<style>
  body{font-family:sans-serif;margin:2rem;max-width:400px}
  button,input{margin:0.3rem;font-size:1rem}
  #info{margin-top:1rem}
  #error{color:red;aria-live:polite}
</style>
</head>
<body>
<h1>Water Tracker</h1>

<div>
  <button id="b250">250 ml</button>
  <button id="b500">500 ml</button>
  <input type="number" id="custom" placeholder="ml" min="1" max="2000">
  <button id="addCustom">Add</button>
</div>

<div id="info">
  <p>Total today: <span id="total">0</span> ml</p>
  <p>Goal: 2000 ml</p>
  <p>Completed: <span id="percent">0</span>%</p>
  <p>Remaining: <span id="remain">2000</span> ml</p>
  <p>Streak: <span id="streak">0</span> day(s)</p>
</div>

<button id="reset">Reset today</button>
<p id="error" role="alert"></p>

<script>
/*--- persistence ---*/
const KEY='waterTracker', GOAL=2000;
function todayISO(){return new Date().toISOString().split('T')[0];}
function load(){const s=localStorage.getItem(KEY);return s?JSON.parse(s):{todayDate:todayISO(),todayTotal:0,streak:0};}
function save(s){localStorage.setItem(KEY,JSON.stringify(s));}

/*--- pure logic ---*/
function isValid(v){const n=Number(v);return Number.isFinite(n)&&n>0&&n<=2000;}
function addDrink(st,amt){if(!isValid(amt))return st;return{...st,todayTotal:st.todayTotal+Number(amt)};}
function resetToday(st){return{...st,todayTotal:0};}
function calc(st){const total=st.todayTotal, rem=Math.max(GOAL-total,0), pct=Math.min((total/GOAL)*100,100);return{total,rem,pct};}
function dayChange(st){if(st.todayDate!==todayISO()){
  const newStreak=st.todayTotal>=GOAL?st.streak+1:0;
  return{...st,todayDate:todayISO(),todayTotal:0,streak:newStreak};
}return st;}

/*--- UI ---*/
let state=dayChange(load());
render();

document.getElementById('b250').onclick=()=>handle(250);
document.getElementById('b500').onclick=()=>handle(500);
document.getElementById('addCustom').onclick=()=>handle(document.getElementById('custom').value);
document.getElementById('reset').onclick=()=>{state=resetToday(state);save(state);render();};

function handle(v){
  const prev=state.todayTotal;
  state=addDrink(state,v);
  if(state.todayTotal===prev){showError('Enter 1‑2000 ml');}
  else{clearError();save(state);render();}
}
function render(){
  const p=calc(state);
  document.getElementById('total').textContent=p.total;
  document.getElementById('percent').textContent=p.pct.toFixed(1);
  document.getElementById('remain').textContent=p.rem;
  document.getElementById('streak').textContent=state.streak;
}
function showError(msg){document.getElementById('error').textContent=msg;}
function clearError(){document.getElementById('error').textContent='';}
</script>
</body>
</html>
```

Open the file by double‑clicking it in your file explorer.