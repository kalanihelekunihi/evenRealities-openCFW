# GoMore algorithm coordinator dependency audit

REA decompilation of stock `0x5ff94` (1,606 bytes), called by the host adapter
with context+320 and an index delta, exposes sixteen work stages plus the
`0x578c8` marker/no-op entry. The [receipt](gomore-algorithm-dependency-audit.json)
records the exact source artifact, REA evidence, pseudocode hash and seventeen
provider inventory rows. This is a pseudocode-derived audit, not a C candidate.

The repeated stage pattern reads a live control byte, calls the provider with
the supplied delta for state zero or delta one for state one, changes state one
to zero after the call, changes state two to three without calling, and writes
the low result byte to a stage status. Other control values appear to suppress
the provider and publish zero. Each stage then calls the marker entry. These
conditions, load ordering, arguments and mutation behavior need instruction and
native/C replay confirmation before implementation.

The stages cover respiratory rate, locomotion preprocessing, classification,
SPS accelerometer processing/selection, sleep motion, heart-rate selection,
energy, dormant estimation, motion gating, sleep cycle/optical peak/staging,
activity windows, step accumulation and activity accumulation. Their existing
manifest/frontier entries are compiled-symbol hints, not verified stock ABI
providers. Reuse requires per-provider ABI review and consolidation rather than
blindly wiring the generic functions into the coordinator.

The activity-window stage `0x6138c` takes a float-converted unsigned delta in
the pseudocode, unlike the other integer-delta stages. Confirm hard-float register
placement and FPSCR timing from instructions. Several stages have more than four
integer arguments; confirm stack-slot order, late alias reloads and post-call
state clears. The marker has an existing generic no-op owner; verify its exact
native leaf before sharing that implementation. The apparent raw return pointer
must also be checked rather than inferred as a semantic algorithm status.

Next work is to freeze those instruction-level contracts, define the native C
interfaces and a mutation-aware ordered-call oracle, then consolidate the generic
orchestrator owner. No algorithm coordinator source, source manifest or canonical
image selection changes at this checkpoint. Physical validation, source-only
link completion and byte identity remain separate gates.

The subsequent [typed C investigation](gomore-algorithm-c-investigation.md)
confirms stage ABIs and live-state ordering through 4,512 native/C cases; the
candidate remains experimental pending promotion checks.
