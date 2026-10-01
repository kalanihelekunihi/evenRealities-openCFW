# Independent review 1825: case csky status decode independent review 1825

Status: **PASS_SCOPED**. Accepted: **no**.

## Checks

- Candidate verifier passed, reproducing source-image/body/gap hashes, exact C-SKY disassembly, caller edges, branch fixtures and parent-composition checks.
- Independently inspected both decodes: each snapshots 0xA0000034 once and tests bit priority 0,2,3,1 with returns 2,3,5,4; only the all-clear path reads 0xA001002C and returns bit 0. Incoming R0 is not read by either body.
- A and B spans are separate conditional image mappings, each 66 bytes; following zero halfword is retained as an unowned BKPT seam. Similar behavior does not prove shared physical code.

## Limits

- Conditional A/B image mapping, physical loading, and visibility remain unverified.
- MMIO meanings/effects are unknown; no physical execution claim.
- Other direct callees and stage-two coverage remain open; no canonical admission.
