# Private P2 correction: controller-to-buffer receive 1465/003

This append-only attempt corrects the ready predicate from attempt 002. Original instruction C0C is `ANDI R2,R2,8`; C10 branches back when that result is zero, so the receiver waits for bit 3 set. Attempt 002 is preserved and its receipt hash is pinned in `input-pins.json`.

Run `python3 verify.py` here. Verification decodes the original locked bytes, asserts the exact ANDI immediate and BEZ target, and reruns nine finite traces including bit1-only and bit2-only counterexamples.
