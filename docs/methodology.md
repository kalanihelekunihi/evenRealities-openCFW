# Methodology

Both targets reconstruct firmware for hardware whose source is not published.
The shared discipline is that **every claim is backed by an artifact a reader
can re-derive**, and anything not backed that way is recorded as an open gap
rather than filled in with a plausible guess.

The two targets apply that discipline differently, because they are solving
different problems.

## G2: byte-exactness as the invariant

G2 works backwards from the official image. The build reconstructs the stock
flash layout exactly, then replaces reconstructed regions with compiled source
one closure at a time. The invariant is that the produced package stays
byte-identical to the reviewed reference at every step.

That invariant is what makes incremental replacement safe. A region is only
promoted to compiled source once the compiled output occupies the same bytes as
the region it replaces, so a promotion cannot silently change behavior. The
consequence is that the toolchain is part of the specification: overlays are
pinned per reviewed compiler profile, and a compiler outside the reviewed
release family is rejected rather than accommodated.

Progress is therefore measurable rather than impressionistic.
[`../g2/docs/source-coverage.md`](../g2/docs/source-coverage.md) records exactly
which functions are compiled from source, and
[`../g2/docs/upstream-inventory.md`](../g2/docs/upstream-inventory.md) records
the attribution queue.

## R1: contract equivalence as the invariant

R1 has no byte-exactness goal and makes no claim to one. It reimplements the
*observable* firmware contract — the EUS transport, checksum schemes, command
dispatch, storage layouts, notification queues, and health pipelines — from
recovered evidence, and verifies that implementation against host tests.

R1 deliberately diverges from the stock image where the recovered behavior is
unsafe. Those divergences are documented as corrections rather than hidden; the
`kv.bin` power-loss-safe commit/rollover correction in
[`../r1/docs/correlation/KV-STORE-CORRELATION.md`](../r1/docs/correlation/KV-STORE-CORRELATION.md) is a
representative example.

## Attribution: upstream first

Neither target rewrites code that has an attributable upstream. The order of
preference is:

1. **Authenticated upstream source**, pinned to an exact commit and verified
   offline against the reconstructed Git object closure.
2. **A documented port or configuration adapter** around that upstream, owned by
   this project and clearly separated from the upstream boundary.
3. **Clean-room implementation**, only for device-specific behavior with no
   attributable provider.

Every vendored dependency carries a `README.openCFW.md` that states where the
upstream boundary sits and what is project-authored glue — Ambiq and Even ports,
generated schemas, commands, and assets are kept explicitly outside the upstream
boundary. Where a compatible upstream version is selected without claiming it is
the exact vendor version, the snapshot says so rather than asserting a false
version match.

## Provider boundaries: refusing to fabricate

Some functionality depends on licensed third-party providers that cannot be
included: Goodix biometric processing, GoMore health and sleep algorithms, the
YHM power path, the QST accelerometer variant.

For each, the recovered R1-side adapter — power sequencing, lifecycle, register
profile selection, bus arbitration — is implemented and retained, and the
provider itself is an explicit, injectable seam. With no provider bound, the
seam returns `R1_ERROR_UNSUPPORTED`. It does not synthesize heart-rate values,
sleep stages, or battery readings.

This is the single most important behavioral commitment in the project. A
firmware that invents biometric data is worse than one that reports it cannot
measure. The provider-boundary documents under
[`../r1/docs`](../r1/docs) record, per provider, exactly what is implemented
locally and what stays gated.

## Production exclusion

A dependency being present and authenticated does **not** mean it is compiled
into a shipped image. Many vendored snapshots are retained purely as attribution
evidence while their configuration, ABI semantics, or validation remain
incomplete.

This is enforced mechanically, not by convention. Several verifiers implement a
production-exclusion gate that scans the G2 `Makefile`, `manifests/`, and
`components/` for references to the snapshot and fails closed unless the only
matches are an exact allow-listed pair of metadata lines. Promoting a dependency
to production is a reviewed change to its verifier and its `README.openCFW.md`,
not a build flag.

Read each dependency's own status before assuming it ships.

## Verification is self-referential on purpose

The test suite does not only test the firmware; it tests the verifiers. 61 test
modules check the snapshot verifiers themselves, and several pin a verifier's
exact byte size and SHA-256. Two modules pin the SHA-256 of `g2/README.md` and
the G2 `docs/*.md` evidence documents.

This makes some ordinary-looking edits fail the suite, which is the intent: those
files are part of the evidence record. It also means the layout of the tree is
itself pinned — see the note in
[`repository-layout.md`](repository-layout.md#third-party--shared-dependency-registry)
about why the vendored snapshots are not relocatable without retiring the
guarantee they exist to provide.

## Evidence provenance

Recovered evidence — decompilation corpora, Ghidra BSim correlations, emulation
models — was produced in a separate research workspace. Where an R1 document
cites an analysis script by a `scripts/firmware/...` path, that citation names
the tool that produced the evidence in that workspace; it is provenance, and it
is left exactly as written rather than rewritten to point somewhere in this
repository. Raw run artifacts (Ghidra logs, correlation CSVs) are regenerable
and not tracked here; their hashes and conclusions are recorded in the
correlation documents.
