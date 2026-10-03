# Independent review 2889, endpoint-validation follow-up

Status: **PASS_SCOPED** (`accepted: false`).

This report binds to corrected candidate `analysis/whole-campaign-admission-frontier-2888/002`. The replay's pinned workflow state, image inventory, coverage inventory, and identity file hashes match. The 33 image-content pins and candidate artifact hashes verify. Isolated replay passed with 70 coverage rows, 40 scopes, and 43 unknown rows.

The correction closes the endpoint finding from review 2889/001. It authenticates the bundle and six payload/component files from `identity.json`, binds the 40 coverage scope IDs to authenticated file extents, and checks each scope starts at zero, has adjacent intervals, and ends exactly at its bound file size. This also correctly distinguishes the `apollo_main` outer component from the smaller extracted `apollo_main:flash` image. Unknown spans and byte counts remain per-scope; nested extents are not summed as progress.

This remains a private navigation/accounting audit. Canonical-record presence checks cover only the stated root and inventory locations, and no semantic coverage, whole-corpus completeness, gate completion, or canonical admission is claimed.
