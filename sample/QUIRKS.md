# Known quirks of InvoiceCalculator

Each quirk is real behaviour finance depends on, and each is a trap for a
reasonable-looking modernization. `harness/mutants.json` breaks each one in
isolation; `ControlQuirksTest` is the hand-written check for each.

| ID | Behaviour today | The tempting "cleanup" that breaks it |
|---|---|---|
| Q1 | Line totals and tax use banker's rounding (`ROUND_HALF_EVEN`): 0.125 -> 0.12 | Replacing the deprecated constant with `RoundingMode.HALF_UP` |
| Q2 | Volume discount starts at 11 units (`> 10`), though the javadoc says "10 or more" | "Fixing" the code to match the comment |
| Q3 | Customer types are trimmed and case-insensitive (`" wholesale"` is wholesale) | Turning the if/else chain into a `switch` on the raw string |
| Q4 | A due date on a weekend rolls forward to Monday | Rewriting `Calendar` code with `java.time` and dropping the rollover |
