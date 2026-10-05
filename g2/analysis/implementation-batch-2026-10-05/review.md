# Independent implementation review

Scope: read-only review of `g2/tools/preserve_l8_resources.py`, its resource map, their tests, `components/foundation/touch_scb`, the touch tests, and Makefile integration. No implementation or shared state was changed.

## Findings

No critical data-integrity or destructive-output defect found in the reviewed paths.

The L8 tool pins the exact map bytes and payload digest, validates descriptor and pixel hashes, checks geometry, bounds and runtime/payload address conversions, rejects overlapping descriptor/pixel regions, and verifies local `.l8` and PGM files before repacking. Repack uses exclusive output creation and verifies the entire result is byte-identical to the input payload. Export stages its files and refuses an existing destination. The tests exercise exact repack, wrong payload, malformed descriptor geometry/pointer/overlap, tampered local resources, and existing-output preservation.

One recoverability edge remains: export creates the destination directory before renaming staged files into it. If a rename or filesystem operation fails after that point, the destination may remain partial and prevent a clean retry. This does not overwrite existing user data, but rollback/removing only the newly created empty-or-partial destination would make failure recovery clearer.

The touch wrapper matches the documented recovered behavior: read status, mask to nine bits, clamp to the request, call the injected transfer exactly once (including zero), return the clamped element count. The six original-instruction cases are appropriately bounded at a callee-entry stub; they validate wrapper arguments/return behavior, not FIFO/MMIO or the callee implementation. The component and README do not claim a hardware provider or MMIO implementation.

The checked adapter validates pointers/callbacks and element widths, computes at most `511 × 2` bytes without overflow, checks capacity, and leaves `actual_out` untouched on failure. It performs the status callback before checking destination capacity. The README accurately warns that a real status read may have device effects; callers should treat the status callback as potentially side-effecting. If callers need invalid-capacity rejection before any device access, the current API cannot provide that without changing the contract or passing a known bound.

The earlier test-quality limitations are fixed in the current test: the SCB handle is now a direct `void *`, and the width-2 check uses an eight-byte destination. The host test compares all eight original-instruction cases (the six prior cases plus held-out equal-count and maximum-request cases) against persisted validation data. It also checks zero-capacity empty success, missing status/transfer callbacks, capacity rejection, and unchanged `actual_out` on errors. The original-code validator records 119 events; every wrapper instruction is checked against authenticated bytes, while the transfer callee remains stubbed at entry.

## Integration and claim limits

The resource targets are optional and separate from the official reference-bundle builder/provider. `foundation-test` runs both new test modules; `core-test` includes them. The new resource unit tests are synthetic and do not require the official payload. The resource map keeps vendor-rights limits explicit. The partial-export recovery edge is now documented in `g2/tools/RESOURCE_PRESERVATION.md`: verification rejects incomplete output, retry should use a new destination, and there is no automatic cleanup. The new `foundation-object` Make target compiles the touch wrapper as freestanding C11 for Cortex-M0+ with warnings-as-errors; it creates no firmware link/provider. The parent reports this target passed. The touch source identifies itself as new MIT reconstruction and points to upstream correspondence while noting the neighboring function is not a compiler-byte match.

Do not describe either addition as a complete firmware source rebuild or byte-identical source reconstruction. The resource repack proves exact preservation of the six extracted regions and whole-input byte identity; it does not replace the official provider. The touch tests establish the recovered wrapper's bounded behavior only, with the transfer callee stubbed and no MMIO/device build.

## Verification

Static review only; the parent reports the resource path, final tests, and foundation-object target passed. No shared test run or output generation was initiated by this review. Current implementation hashes: resource tool `79cd528d9490bef6ca8d56fe5bd34d6a87bc26e7aee3dfda8f095ec6b29eaf7d`; resource map `33115d16c9917b0908943c4f2c91b0f8955b3b255bf5a06fe10adf736841595d`; touch C `ef593088ec3c20985ae8c4b51cf932d9ccc9a98627b43dbe08e8befa412d8afd`; touch header `92e7b7a09807209efba8b0372e615dd3b5ab32dd0459bc4c25675392e29b525d`; touch host test `59b4695de6483dd2ec081ba6468be82d0f2e3a806a2793ee2760876560435e6b`; resource test `c4fb21e73ba188b8d900e0643fc81801c286977c9809e99a300dd2217433004a`; Makefile `cbf22795e495f2dae520868c668b71372f4090f77953a4f7fa042ef9b4d00aeb`.
