# P2-9033 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- The two four-pointer tables and eight BX LR bytes match the pinned image; each default table entry points to a two-byte no-op return stub.
- The packet separates 32 table-data bytes from eight code bytes and distinguishes the high-category direct callback slot (+76) from the category tables.

Limitations:

- Only the currently published default targets are classified. Replacement behavior, concurrency, and whole-firmware coverage are not established.
