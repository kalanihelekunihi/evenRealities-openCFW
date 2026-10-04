# P2-9091 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- All 162 mapped instruction bytes across both builders match the locked image.
- The first builder requests zero-payload type 0x200E and returns saved entry R7, skipping dispatch on null allocation. The second requests type 0x2020/length 14, delays loading three stack arguments until allocation succeeds, then writes seven low16 scalar fields to bytes 3..16 and dispatches.
- For the scalar builder, saved entry R3 (fourth register argument) is restored into R0 at return; child dispatch status is discarded. Upper halves of scalar inputs are ignored.

Limitations:

- Allocation and dispatch contracts are unresolved; no pointer checks or packet semantic interpretation are claimed. Synthetic/reversible map evidence only, not concurrency/physical behavior.
