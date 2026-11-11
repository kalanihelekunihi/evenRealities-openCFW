# R1 shared DFU SVCI state ownership

`native_dfu_svci_owner.c` compiles the unmodified pinned
`ble_dfu_unbonded.c` implementation once and exports its private asynchronous
state through the compiler alias `r1_dfu_svci_async_state`.
The recovered backend now references that same allocation. Previously it
imported the SDK's static name as an external symbol, leaving that import
unresolved. A separate zeroed object would have split initialization and use.

The alias preserves the SDK C type and its 12-byte layout: asynchronous function
at offset 0, event handler at 4 and state at 8. Compile-time assertions and the
linked ELF check confirm one 12-byte allocation. Clang canonicalizes the alias
as the global name; the private identifier does not create another allocation.
This compiler extension remains specific to the verified toolchain.

REA/Ghidra stock reads confirm that the SDK initializer and recovered backend
use the same native address, `0x2002c12c`. The stock system-event path also loads
that address. Executing the locked firmware's zero-initialization handler
confirms the state begins as twelve zero bytes; the whole zero region and
adjacent guards were checked. Test placement at the native address does not
establish a final source link.

The actual normal-build owner and backend passed 1,728 paired stock/C sequences.
They execute SDK initialization, conditional asynchronous name dispatch and
system-event invalid-state handling. Cases vary vector set/unset statuses,
SVCI status, partial callback installation, asynchronous statuses, busy flags
and PRIMASK. The modeled SVC0 resolver checks SVCI number 3 and the shared state
address. Both callbacks receive the same state word at offset 8, mutate it and
leave matching state/context bytes. Returns, provider order, callee restoration,
SP and interrupt masks are checked. Three negative controls reject detached
storage, the wrong state pointer and an incorrect SVCI number.

Provider frames are recorded rather than equated: for example the native/C
asynchronous callback depths are 16/8 bytes and event callback depths are
16/56. Logging is exercised in silent mode. Resolver/callback providers and
vector set/unset are modeled. Event success/error responses, physical flash
writes, supervisor/exception behavior and real DFU operation remain unproven.
Nonargument caller-clobbered values, live callee register values, private spills
and APSR are excluded.

The full R1 build compiles/composes 590 units without known failures or duplicate
strong symbols. Application imports fall from 163 to 162; bootloader imports
remain 34. The other 588 objects are byte-identical. After normalizing the owner
name, both changed units retain identical allocated sections and relocations.
The upstream SDK source is unchanged. The SDK initializer frontier span is also
corrected from 162 bytes, which included later functions, to its 32 code bytes
before the four-byte address literal.

Exact qualification selected no new regions. The source plan and hybrid
application hash remain unchanged, with 4,245 source-built, 641,915
binary-pull-through and 248 resource bytes. This closes a composition dependency;
it does not prove source completeness, a complete source link, physical hardware
support or a byte-identical source rebuild.

The [receipt](dfu-state-owner-review.json) records sources, compiler arguments,
hashes, stock evidence and test results. Ignored reproduction inputs are under
`build/goal-r1-dfu-state-owner/`. Current reports are
`build/sources-goal-r1-dfu-state-owner/report.json` and
`build/hybrid-goal-r1-dfu-state-owner/build-report.json`.

The backend now uses [typed Nordic SVC APIs](dfu-backend-sdk-c-review.md).
The shared-state regression above passes again against that normal product build.
