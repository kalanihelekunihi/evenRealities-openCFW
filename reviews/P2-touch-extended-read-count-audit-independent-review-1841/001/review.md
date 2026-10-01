# Independent review 1841: scoped evidence pass

Status: **PASS_SCOPED**. Accepted: **no**.

## Checks

- Audit hashes and its exact parent receipt/replay pins verified. An isolated run counted original 810C calls and 8394 candidate comparisons in each of 120 delimited 8352..83F2 segments; generated audit JSON matched byte-for-byte.
- Maximum observed advances/checks is four for context count four. The instruction order confirms count check before stepping, with index increment only after candidate rejection. This refutes count-minus-one for these traces.

## Limits

- Every audited search found a candidate; no-match exhaustion is unexercised here (separate trace packet covers it). Audit only answers bounded search-count behavior; no global recovery or physical storage claim.
