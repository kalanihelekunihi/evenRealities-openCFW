# Independent review: bounded Ambiq MSPI subset

## Result

No critical correctness, license, or evidence-integrity defect found in the reviewed snapshot. The four selected interrupt routines retain their pinned upstream function text; their register operations and ordering agree with the official firmware instruction traces across the saved linked-original comparison. The implementation remains a narrow callable source subset, not a complete HAL, hardware validation, or byte-identical firmware claim.

## Checks and evidence

- The function text hashes in `SOURCE_PROVENANCE.json` match the four function excerpts in `ambiq_mspi_interrupts.c`. Both derived source files retain the Ambiq BSD-3 copyright, conditions, and disclaimer. The cached upstream evidence identifies the public Ambiq 5.1.0 API source revision and explicitly separates its provenance from proof of the private firmware-producing revision.
- Compatibility declarations cover only the first eight handle bytes and the interrupt-register window. Static assertions pin the prefix/module/register offsets. The documented API preconditions are material: callers must provide a readable aligned handle, initialized prefix, module 0–2 with mapped/powered registers, a writable aligned output pointer for valid status calls, and serialization against concurrent handle/configuration/INTEN writers. The reused upstream routines do not validate module range or status-output pointers.
- The current `comparison-heldout.json` is `PASS`, contains 68 cases and 230 unique original instruction bytes, and matches the current verifier, source manifest, parser, and linked ELF hashes. Per-operation coverage includes all three modules, masks including `0x1a80`, both status interpretations, invalid/null handles, malformed prefixes and reserved/high-bit variations. The verifier compares return values, MMIO read/write sequence and values, output guards, and final registers between original instructions and the linked callable module.
- `INTCLR` behavior is modeled with a synthetic W1C hook that clears matching `INTSTAT` bits. The report correctly limits that result: no powered hardware, posted-write behavior, clock/IRQ timing, or interrupt delivery is established.
- `python3 -m unittest g2.tests.test_ambiq_mspi -v` passed all four tests: three-module host fixture behavior, Cortex-M55 linked entry bounds, upstream excerpt hash/license retention, and fail-closed rejection of optimized Python. The Makefile integrates the test and standalone simulator build/run targets without adding the module to firmware production sources.

## Remaining limitations

The exact-function hash test relies on the checked-in provenance JSON; upstream authenticity is supported separately by the upstream evidence report and pinned API-tree blob identities. The comparison script records current source hashes but creates its report with exclusive-create semantics, so repeat runs need a new output path. The public SDK snapshot establishes source-level compatibility only; it does not establish the actual private build revision/compiler/options. Handle memory validity, module/power state, concurrency, and MMIO side effects remain caller/hardware obligations.

## Snapshot identities

- `ambiq_mspi_interrupts.c`: `032087d41fe463a36c6a119b8fd2a7beb1256356e2f6d8d9d7f4ca75e02e5ba3`
- `ambiq_mspi_compat.h`: `abbd8b8e201246c927125d7ab5cd900bf510e211ec901278961523104099f7cb`
- `simulator/verify.py`: `adc66c4a1506425ca1b2c526da46a842e3ef5c0844a7dde3a76ce5a53147aa26`
- `test_ambiq_mspi.py`: `7681604c3d90f58addd1e56ac681303964fcd747cda7e86c84a5e25ab1be82d6`
- `Makefile`: `673d6ec5fb4cc30610b1d811aefa64abe587ba5d5d11eb54537a1c4b834e74d2`
- linked ELF: `a4d2c11d28a9b1f94662defb06de6caff8d29620634b5acf9d36028e8f529458`
- comparison: `71c795d4b481273c924cf26745f804b82c0ac71f02713d85056f037ddf68dcff`
