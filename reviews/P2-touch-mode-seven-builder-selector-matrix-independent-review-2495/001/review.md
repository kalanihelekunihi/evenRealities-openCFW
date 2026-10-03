# Independent review 2495

**Result:** PASS_SCOPED.

Candidate `analysis/touch-mode-seven-builder-selector-matrix-2494/001` receipt SHA-256 `6cbcf8a5c53a7cd75934d9e5ffff42f47398a654b4255993622d50f7323e12ec`; all declared artifact hashes and both owned spans validate against the pinned source image. The isolated replay passes all 576 fixtures.

The original mode-seven chain executes without firmware interception. The matrix varies byte117 selectors 0/2/5 and byte116 selectors 0/2/4 across validity branches, prior modes, and the other fixed builder inputs. The asserted builder model matches the selector-derived mode choices, per-validity secondary/group modes, cached old-word clear/OR behavior, full ordered write ledger, complete 224-byte buffers, child arguments/order, final mode/status/config flags, delay count, and R4–R11/SP. Prior mode 7 equality bypasses all builder calls and writes.

**Limits:** Constructor fields and list contents remain fixed; factory/MMIO values are modeled and peripheral writes are diagnostic rather than a fully asserted ledger. Alias/concurrency behavior and physical timing are not established. Dependency execution does not establish ownership. Accepted:false; private scoped evidence only, no canonical admission.
