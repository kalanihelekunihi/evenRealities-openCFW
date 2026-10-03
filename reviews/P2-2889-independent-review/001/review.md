# Independent review 2889

Status: **REVISE_SCOPE_VALIDATION** (`accepted: false`).

The candidate artifact hashes match and the isolated replay passed: 33 inventory images, 70 coverage rows, 40 scopes, and 43 unknown rows. It verifies each inventory image's content hash and checks that coverage intervals begin at zero and are adjacent.

The replay does not compare each scope's final coverage end with that scope's authenticated file extent. A contiguous prefix could therefore leave a trailing portion unrepresented while still producing the scope summary. Keep this revision's result limited to interval adjacency until authenticated endpoint validation is added.

The report correctly avoids summing nested bytes as package progress and explicitly limits canonical-record presence checks to campaign-root and inventory paths. It makes no semantic-coverage or admission claim.
