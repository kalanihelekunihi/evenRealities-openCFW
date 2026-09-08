# GX8002 SNPU suspend candidate

The reconstructed C candidate fits 72 bytes at runtime `0x10205a90`
(package `0xf01c`) with the original eight-byte frame. It is qualified and
registered in the integrated builder; all 385 integration tests pass.

The observed state base is `0x20027350`. It reads a pointer at offset `0x5c4`
first and returns -1 if null. Otherwise it reads the state word at offset0,
and returns zero without helper calls if that word is2. For other states it
calls `npu_is_enabled` with the first pointer. If enabled, it reloads the
pointer, calls `npu_disable`, then reloads the pointer for every
`npu_get_all_idle_status` poll until a nonzero response. Finally it calls
`gx_clock_set_module_snpu_enable(0)`, writes state2, returns zero.

The source preserves these live pointer reloads and indefinite wait. Its
structure is an offset view over external state, with an explicitly unmodeled
gap. This does not claim source ownership or understanding of that gap.
The upstream driver object identifies helper names via relocations and is
never linked into the firmware candidate.

Required next checks: compare stock/source against independent call and
state traces, varying null/non-null initial pointers, state values, enabled
responses, helper-driven pointer/state changes, delayed/never-ready idle
responses, helper clobbers, return values and stack preservation. Source
internal prototypes currently encode observed calling contracts; qualify
helper implementations separately. Candidate evidence is
`gx8002-snpu-suspend-candidate.json`.

```sh
python3 g2/tools/build_gx8002_snpu_suspend_candidate.py
```

A limited public web search for the NationalChip SNPU suspend implementation
and `npu_get_all_idle_status` did not locate matching C source. It surfaced
NationalChip's Fornax application documentation (a different chip family),
which is not sufficient evidence for substituting GRUS driver behavior. This
search does not prove that source is unavailable elsewhere; retain the pinned
object identity and stock behavior as current evidence.

The candidate has now passed decoded stock/source comparisons against an
independent state/call oracle: 3,024 completed cases and 54 never-ready polling
prefixes. Ten regression tests pass. Initial null pointers, state2 fast return,
nonzero enable responses, delayed idle responses, alternating helper-driven
pointer changes and helper-driven state changes are modeled. The clock call
can modify state before the final source store overwrites it with2. Both
implementations preserve their eight-byte frames and saved registers.
The idle poll retains the original unbounded wait; prefix checks cover up to
32 never-ready polls and do not establish physical timing or completion.

Reproduce qualification:

```sh
python3 g2/tools/verify_gx8002_snpu_suspend.py
python3 -m unittest discover -s g2/tests -p test_gx8002_snpu_suspend.py
```

Evidence: `gx8002-snpu-suspend-verification.json`.
