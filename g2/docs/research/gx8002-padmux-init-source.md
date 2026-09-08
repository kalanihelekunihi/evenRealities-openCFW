# Padmux initializer reconstruction

The routine at package 0xfbbc / runtime 0x10206630 rejects null configuration
pointers and negative counts. Otherwise it iterates the 32 default entries,
searching the caller's table from the beginning each time. The first matching
pin overrides the default function; unmatched pins use function zero. It calls
the setter for each default pin and ignores its return, returning zero after
all 32 calls. A non-null empty table applies defaults; a null empty table fails.
Pin 32 is absent from this table even though the individual accessor accepts it.

The 64-byte table at package 0x14250 / runtime 0x1020acc4 is exactly the typed
sequence {pin, function=0} for pins 0..31. This matches the authenticated SDK
object's .rodata, and the independent semantic generation matches stock.
runtime_gx8002_padmux_defaults.c expresses the policy as typed C entries.
Neither source file imports binary bytes.

The initializer builds natively on macOS to 72 bytes within the 80-byte stock
region. It currently binds the default-table and setter addresses; the default
C object still requires placement qualification, and initializer decoded
memory/call/ABI qualification is pending. It is unregistered and not hardware
qualified. Valid caller tables must be readable arrays without pointer-wrap;
concurrent mutation and malformed pointers are not yet qualified.

Decoded stock/C execution passes 529 cases with exact byte-read and setter-call
traces, including full ascending/reversed override arrays, duplicate overrides,
out-of-default pins, singleton function boundaries, null pointers, negative
counts and modeled setter failure. The interpreter checks the optional 20-byte
frame, preserved ABI registers and hostile caller-register clobbers. Four focused
tests cover first-match selection, ignored setter failure, null/empty distinction
and wrong helper target. Decoded setter-body composition remains pending.

The default table now has a reproducible verifier,
verify_gx8002_padmux_defaults.py, which authenticates the SDK header, compiles
the typed C policy, checks all 32 entries and absence of relocations, compares
the independently compiled result against stock evidence, and exports a
source-data placement row. Three policy mutation tests pass. This table is
qualified for source admission but remains unregistered pending integration.

Initializer/setter decoded composition passes 96 scenarios and 3,072 setter
calls. Register words persist across pin updates, and the final values match
an independent first-override/default policy. All four stock/C outer/helper
selections pass with success and failure checker results. Six focused tests
pass after adding the setter hook. Checker results remain modeled in this
composition; full initializer/setter/checker/getter chaining is still pending.

Full decoded initializer/setter/checker/getter composition now passes 384
scenarios and 12,288 setter calls across all sixteen stock/C selections. Checker
and getter bodies execute at their call boundaries, with written or inverted
readback supplied explicitly. Persistent register writes match the independent
pin policy. Helper stacks remain separate; this does not prove nested stack
sharing, concurrent access, or physical pad effects.

The initializer admission verifier now exports its linked artifact and placement
row, includes the full decoded composition and compiled default-table policy,
and pins ten verifier/builder evidence files. Requalification passes 529 direct
cases plus 384 full-chain scenarios. All 26 padmux focused tests pass. The
initializer is source-admitted for its stated valid-array contract but remains
unregistered until the current package build/verification is complete.
