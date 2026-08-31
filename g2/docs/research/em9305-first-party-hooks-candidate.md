# EM9305 first-party hook-span clean-room candidate

Status: software-only, fail-closed candidate; not production-routed

License: MIT

Hardware activity: none

## Result

The seven first-party residual spans now have an isolated OpenCFW source
model and machine-checked evidence map.  The candidate intentionally separates
control flow proven by authenticated ARC instructions from behavior that is
still unknown.  It does not copy stock application code and does not make an
unverified semantic claim merely to fill the retained ranges.

| Stock range | Bytes | Evidence-backed role | Candidate model |
|---|---:|---|---|
| `[0x0030482C,0x003048AE)` | 130 | startup-hook target and 912-byte-stride accessors | provider required |
| `[0x0030EA08,0x0030EB0A)` | 258 | `MyApp` active-object cluster, assertion ID 181 | provider required |
| `[0x0030EB8C,0x0030EC9A)` | 270 | hook-table vendor resume extension | provider required |
| `[0x0030ECF8,0x0030EF12)` | 538 | hook-table vendor startup extension | provider required |
| `[0x00311150,0x00311154)` | 4 | `QF_onResumeInternalHook` tail branch to `0x00310798` | exact branch shell; target provider required |
| `[0x003111A4,0x003111A8)` | 4 | `QF_onStartupInternalHook` tail branch to `0x0030482C` | exact delegation to the modeled target span |
| `[0x00311620,0x00311634)` | 20 | `QK_onIdleInternalHook` | exact three-call shell |
| **Total** | **1,224** | first-party application | fail closed |

The source lives in:

- `components/shared/em9305/runtime_first_party_hooks_candidate.c`
- `components/shared/em9305/runtime_first_party_hooks_candidate.h`

No component Makefile, overlay, package manifest, or production ledger routes
these files.  Their callbacks use an OpenCFW-owned adapter contract rather
than pretending that the stock C prototypes are known.  Missing providers,
invalid arguments, and provider failures have distinct statuses.

## Exact control flow retained in the model

The startup internal hook is a single authenticated branch to the first span,
so the candidate delegates to that same typed boundary.  The resume internal
hook similarly delegates to a provider for the authenticated `0x00310798`
target, which is outside this seven-span tranche and remains unresolved.

The idle hook has one fully bounded shell:

1. call `0x00333D7C`;
2. call `0x003100EC`;
3. call `0x00310728` with `r0 = 0` in the delay slot;
4. return.

The initial generic candidate verifies all three providers before the first
call. A subsequent authenticated SDK archive comparison narrows the first
callee to `wsfOsRunIdleTasks`, the
second to `VoltMon_DoMeasurement(0)`, and the resume target to
`PalUartResume`; the final idle edge is an exact no-op chain. The named adapter
preserves the stock unconditional call sequence and treats the WSF return as
an activity bit rather than an error. See
`em9305-qpc-hook-provider-closure.md`. Clean-room MIT source is now available
for WSF idle tasks, while the hardware-specific UART and voltage-monitor
providers keep the complete shell ineligible for production.

## Evidence and reproduction

The read-only analyzer authenticates:

- the complete official EM9305 image and whole-application ARC objdump;
- the exact bytes and SHA-256 of all seven spans;
- the existing high-confidence residual-provenance rows and 1,224-byte total;
- the nine-entry QF/QK hook pointer table and target order;
- both tail-branch targets;
- the four 912-stride multiply sites in the startup target;
- the `MyApp` assertion call and immediate ID 181;
- the first resume-extension call to authenticated `BSP_Init`;
- the idle call order and its final zero argument; and
- the candidate's MIT declarations, API, evidence descriptors, and
  fail-closed model markers.

```sh
python3 tools/analyze_em9305_first_party_hooks_candidate.py --json
python3 -m unittest -v tests.test_em9305_first_party_hooks_candidate
```

The host suite also compiles the code freestanding with warnings as errors,
checks that the object has no undefined runtime imports, exercises every
missing-provider path, proves argument-carrier forwarding, checks startup
tail delegation, and validates idle preflight/order/failure behavior.

## Integration blockers

1. Recover independently reviewable behavior and exact ARC ABIs for the four
   provider-required first-party clusters.
2. Bind the clean-room `wsfOsRunIdleTasks` provider to exact ARC state and
   placement contracts; implement `VoltMon_DoMeasurement` only from authorized
   physical platform evidence.
3. Recover redistribution-safe exact source and ABI semantics for named resume
   target `PalUartResume` at `0x00310798`, including its argument, return,
   power-state, and ordering contracts.
4. Define clean-room `MyApp` active-object state, event allocation/dispatch,
   pool ownership, and assertion policy.
5. Authenticate final link placement, relocations, callback registration,
   startup ordering, and complete software test coverage before routing.

No directed hardware test is needed or performed in this tranche.
