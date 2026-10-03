# Independent review 2657: stepwise dispatch with authenticated table

**Result: PASS_SCOPED.** `accepted` remains false.

The exact body and source pins match. I independently decoded the step loop and reran all 1,600 fixtures in isolation. The actual table is loaded from decoded RAM at `0x20000158`; entries 0–23 are controlled at their authenticated addresses, while entries 24–26 run the original three `BX LR` instructions. The replay confirms ascending and descending index progression, status-gated dispatch, full final-argument forwarding, continuation after a nonzero route status, and the saved-register return frame.

This establishes bounded routing behavior, not the semantics or extents of entries 0–23. The table snapshot does not prove installation or deployed reachability. The detailed pin bindings and limits are in `review.json`; no canonical admission is implied.
