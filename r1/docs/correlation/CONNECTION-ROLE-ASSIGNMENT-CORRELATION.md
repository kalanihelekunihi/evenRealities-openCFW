# Connection-role assignment correlation

Status: two symmetric R1 product functions / 860 executable bytes byte-pinned; pure fail-closed
assignment policy implemented.

The glasses setter `0x0004D654..<0x0004D802` (SHA-256
`443657cb657e3b72a0a20e7944f95a8f8c0758272157a9b0758ea0882e2c37ba`) and phone setter
`0x0004DA28..<0x0004DBD6` (SHA-256
`51bdbf6412fad98d89416e28326a3735035b9d2e1b8c30d8d2c2edec3c93230e`) operate on the same
role state at `0x200064B2`, with phone handle offset 8 and glasses handle offset 10.

Both reject handle `0xFFFF`, assign only an empty target slot, publish role 1 (phone) or 2
(glasses) only after assignment, ignore a repeated identical assignment, and refuse replacement
when the slot is already occupied. Reusing the other role's live handle enters a fatal assertion
in stock firmware. OpenR1 returns `R1_CONNECTION_ROLE_ASSIGN_CROSS_ROLE_CONFLICT` instead, so
untrusted connection state cannot trigger a fatal callback.

`../src/r1_connection_params.c` implements
only this caller-owned state transition. Nordic connection state, logging, role-event delivery,
and fatal handling remain external. Tests cover assignment, repeat, occupied slot, cross-role
conflict, invalid handle, and null state.

Evidence is reproducible with:

```sh
python3 tools/summarize_r1_connection_role_assignment.py
```
