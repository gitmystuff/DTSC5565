# Project Brief: Water Tracker

## What we want
A tiny web app that helps one person track daily water intake and see progress toward a daily goal.

## Users
A single user on their own laptop or phone browser. No accounts, no sharing.

## Must do
- Log a drink in ml (quick buttons for 250 and 500, plus a custom amount)
- Show today's total, the 2000 ml goal, percent complete and what remains
- Show a streak of consecutive days the goal was met
- Reject nonsense input (zero, negative, over 2000 ml per entry)
- Let the user reset today

## Constraints
- One page: a single index.html with inline CSS and JavaScript
- No backend, no libraries, no build step; must open by double-clicking the file
- Save data in the browser's localStorage
- Plain, readable, accessible design

## Out of scope
Reminders, notifications, accounts, charts, syncing between devices.

## Quality expectations
Include unit-testable logic kept separate from the page display code.
