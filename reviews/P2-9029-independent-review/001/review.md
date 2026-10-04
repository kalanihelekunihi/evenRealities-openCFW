# P2-9029 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- The receipt pins the locked image and its current scope, results, and replay-script hashes; recorded results report 131,072 cases for all 65,536 low-16-bit values in separate and aliased output modes.
- The replay script compares the original decoder against independent divmod expectations, checks remainder then low-byte quotient store order, and asserts preserved R4/R5/SP/PC.

Limitations:

- Unicorn is unavailable in this environment, so I could not independently rerun the 131,072 original-byte cases. This review verifies packet integrity and test/oracle structure only, not fresh execution.
- Synthetic SRAM; no whole-artifact, physical, or unrestricted surrounding-caller claim.
