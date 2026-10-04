# P2-9049 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- Fresh isolated original-byte replay passed all 216 combinations of six record states cubed. The oracle returns the first record with halfword key other than 0xFFFF and nonzero activity byte.
- Full 84-byte table preservation, returned pointer, R4/SP/PC assertions passed; no call substitutions were used.

Limitations:

- Inputs are synthetic stable record states. Concurrent changes between separate key/activity reads and any broader table bounds remain untested.
