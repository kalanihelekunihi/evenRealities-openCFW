# CmBacktrace 1.4.2-compatible source snapshot

This directory is an exact snapshot of the minimal CmBacktrace source closure
selected from official upstream commit
`73714489f9d8af130aacb515586b397b604a5768`. That commit is the newest
unmodified upstream state in the interval proven compatible with the Even G2
`2.2.6.10` image. It is an explicit openCFW reproducibility choice, **not** a
claim that Even used this exact commit or an unmodified upstream checkout.
The upstream header advertises `CMB_SW_VERSION "1.4.2"`, but upstream has no
`1.4.2` tag.

The seven upstream files are the MIT license, core implementation, public and
definition headers, upstream configuration dispatch template, English message
table, and IAR fault entry. Chinese/custom language content, other compiler
fault entries, non-FreeRTOS ports, demos, documentation, host tools, and
packaging files are intentionally excluded.

The snapshot directory itself remains excluded from production compilation.
Its selected MIT commit is now the authenticated compatibility baseline for
the bounded production source adaptation of CmBacktrace's FreeRTOS
`get_cur_thread_name()`, whose selected upstream branch is exactly
`return vTaskName();`. The production copy, port seam, and component license
are pinned in `PROVENANCE.json`; the earlier `_candidate` files remain a
separate, production-excluded research artifact.

The fixed-address `vTaskName` adapter is **not upstream CmBacktrace source**.
It is local recovered G2 integration evidence: the stock adapter loads the
current-TCB word at `0x20074A20`, adds the task-name offset `0x34`, and returns
`0x34` when the current-TCB word is null. OpenCFW's production adapter
preserves those exact semantics without claiming that the address, layout, or
null behavior came from commit `73714489`.

[`g2-config/cmb_user_cfg.h`](g2-config/cmb_user_cfg.h) is openCFW-owned and is
not part of the upstream Git tree. It records the directly recovered FreeRTOS,
stack-dump, depth, and name-size switches. Selecting upstream Cortex-M33 and
English macros is explicitly labeled as a compatibility choice: the retained
behavior does not distinguish an upstream M33 selector from a vendor-added
M55 alias, nor patched English from the custom-language selector. The logging
macro and exact linker-section override spellings remain unresolved, so the
template fails closed until an integration supplies `OPENCFW_CMB_PRINTLN`.

The chosen historical code predates upstream commit `55e7b699`, which added
stacked-xPSR bit-9 exception-frame realignment. The bounded current-thread-name
promotion does not import or decide that fault-frame behavior. Any future
promotion of the CmBacktrace fault core must explicitly choose historical
parity or the newer safety behavior and test both aligned and realigned
exception frames.

Run:

```sh
python3 third_party/cmbacktrace/verify_snapshot.py
python3 -m unittest -v tests.test_cmbacktrace_snapshot
```

The verifier works offline. It reconstructs the selected Git commit and every
required tree, proves commit-to-path-to-blob membership, verifies all snapshot
source bytes and the MIT notice, pins the recovered configuration boundary,
and authenticates the bounded production source/adapter/license records. See
`docs/research/cmbacktrace-version-recovery-audit.md` and
`docs/research/cmbacktrace-get-cur-thread-name-source-candidate-audit.md` for
the upstream and firmware evidence.

The same offline gate scans every source-controlled component `overlay.json`,
every source-controlled manifest JSON, and the top-level `Makefile` while
excluding generated directories named `build` or `build-*`. Path-like JSON and
Makefile tokens are lexically normalized before classification, so redundant
segments cannot bypass the boundary. It rejects direct compilation of this
snapshot, any registration of the `_candidate` paths or symbols, and any
unapproved CmBacktrace production path or symbol. The exact bounded production
helper and recovered-adapter files remain allowed, as does the Makefile's
`cmbacktrace-snapshot` verifier recipe.
