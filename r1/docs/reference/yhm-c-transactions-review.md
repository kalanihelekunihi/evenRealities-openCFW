# YHM read/write transport mapping and wrapper qualification

REA confirms native read `0x507cc` and write `0x50804` use the R1 shared
request/context transport. The write frontier entry previously pointed to an
older generic vendor candidate with a different context API. It now points to
the existing `r1_yhm_register_write_record` C body; the read entry receives the
same current evidence. Firmware C itself is unchanged.

Both paths release the device at context offset twelve, open the currently
cached bus at offset four, then populate three request fields. Read writes a
register byte at zero, data pointer word at twelve and length byte at sixteen.
Write uses offsets zero/four/eight. Other request bytes persist. They reload
the bus for transfer, execute registry slot `0x10` or `0x14` with zero selector,
the shared request and zero extra word, then execute the real completion path.
Completion closes the latest cached bus, reloads the callback and returns the
close/callback raw word. Transfer status does not suppress cleanup or erase
partial driver effects.

The transaction probe passes 7,680 paired stock/C cases (15,360 executions).
It executes actual lifecycle, registry and completion bodies. Device methods
and final callbacks are controlled boundaries. Cases vary full register/length
words, byte truncation, null/non-null data words, two request seeds, callbacks,
raw status words and mutations at pre-close/open/transfer/final-close. It compares
ordered context/request accesses, exact field write widths, retained bytes,
method/callback arguments, data effects, result words and preserved ABI state.
Null data handling is modeled as driver-defined behavior, not claimed physically
safe. Clearing all request bytes is a negative control and fails because stock
retains unrelated shared fields.

An additional 3,840 comparisons (7,680 executions) enter the actual public write
wrapper at `0x35760`. The old inventory assigned it a 78-byte envelope. Independent
REA analysis and raw instructions confirm its full executed body is six bytes:
UXTB R1 followed by a tail branch to `0x50804`; R0/R2 pass through. The frontier
now records this corrected extent as a manual provenance supplement.

Correcting the write binding enables official qualification of
`r1_yhm_register_write_native`. Both Clang and pinned GCC 9 produce the exact
six-byte wrapper with the native write target. Clang's other three selections
are already accepted YHM spans; they are verified duplicate ranges and are not
added again. Neither larger transaction body qualifies. All five Clang and four
supported GCC configurations compile. Qualifier matching/selection logic is
unchanged; only candidate source inputs are filtered.

The nonoverlapping six-byte addition passed a full R1 hybrid build before its
merged plan was promoted. The 646,408-byte output remains byte-for-byte equal
to the locked application, SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
The hybrid report binds the promoted plan hash and expected source provider.
Current source-built accounting is 3,821 bytes: 390 C instruction bytes, 154
source-assembly instruction bytes and 3,277 compiled non-executable bytes.
Resources supply 248 bytes; 642,339 remain unclassified binary pull-through.
The qualified wrapper still branches to retained native write code in this
partial hybrid. Source completeness remains explicitly false.

[Machine evidence](yhm-c-transactions-review.json) binds REA, corrected mappings,
transaction/public probes, negative control, both qualification runs, plan merge,
canonical plan and hybrid output. The build is
`build/hybrid-goal-r1-yhm-transactions`. Source and manifest hashes still match
the normal report: 571 R1 units, 197 application and 34 bootloader imports.
`make sources-check` and diff whitespace checks pass.

Private frames/caller-clobbered registers/flags, concrete callback identities,
arbitrary pointer aliases/faults, concurrency, electrical bus operation, complete
source-only linking/byte coverage and G2 corpus gates remain unverified.
