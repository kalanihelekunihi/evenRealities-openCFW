# Extended logger direct caller inventory

`inventory.py` reads the authenticated 2.2.6.10 main flash and its linear-sweep
disassembly. The stripped main image SHA-256 is
`19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.
It looks backward from each syntactic `bl 0x43d574` for a store into the
stock format slot `[sp,#4]`, then resolves a nearby PC-relative literal load or ADR string.
The exact per-site evidence, recovered strings and conversion signatures are
in `inventory.json`. This is a conservative *literal-resolution* heuristic,
not a proof that a site is reachable or that its argument list is complete.

There are **6,239** syntactic direct BL sites; **6,227** resolve to a readable
literal with this heuristic, spanning **5,032** distinct format addresses.
The remaining 12 use runtime format pointers: four pass the function's R8 format parameter, and eight point to a stack buffer at SP+8. Three formerly unresolved sites use ADR strings (one blank and two `%s`) and are now counted as static. The largest signature groups by
site are: no conversion 2,710; `%d` 1,503; two `%d` 407; `%s` 339; `%x` 120;
`%u` 99; `%p` 26; and two `%s` 19. The image also has floating point formats,
dynamic width/precision, and a 16-`%02X` key dump. These signatures count
consuming conversions, but do not independently establish the stack words at
each call. Examples include `0x43c426` -> `0x75d430` (`AgingTest recv data
len = %d`), `0x43c72a` -> `0x75d4b0` (two `%d`), and `0x49d580` ->
`0x748bec` (three `%f`).

At the time of this inventory, the source formatter initially covered two authenticated SMP literals. A later bounded general formatter is documented in `extended-log-common-format-20261010`.
The new inventory establishes that a whole direct body needs general
`0x44b76c` formatter behavior and a variable-length ARM varargs bridge;
extending the current two-word adapter to the broader callers would invent
semantics. No source/archive change follows from the inventory alone. The
archive currently contains 27 translation units, and direct SMP bodies remain **10/11**.

Fatal level-six stock fixtures already distinguish callback present from
callback missing (`extended-log-policy-20261010/logger_frontier.py`). The
missing callback takes a bounded recursive fatal-loop stop; callback present
reaches the configured callback with assertion arguments. Null module takes
the analogous assertion path in `0x43d4b0`; the callback's return behavior and
subsequent invalid module handling are not an evidenced productive contract.
Neither path justifies a normal-return source implementation yet.

Next bounded experiments: implement and compare general `0x44b76c` formatting
by conversion family (including format flags, widths, precision and floating
point ABI), then recover stack argument counts for representative calls and
validate an arbitrary-length ARM varargs bridge. Independently characterize
the fatal callback's actual installed target and null-module assertion path.
The number of call sites and distinct formats makes this materially larger
than a two-literal extension; no reliable hour estimate follows from current
evidence.
