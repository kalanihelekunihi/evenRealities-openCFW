# G2 Touch source image: production routing and NVIC configuration

Item: TC-001 (`components/touch/source_image -> production provider in a
source manifest profile`). Scope: route the existing 31-translation-unit
clean-room Touch source image
(`g2/components/touch/source_image/`, shared runtime in
`g2/components/shared/touch/`) as the production provider for the `touch`
component, and turn its NVIC vector-slot assumptions into explicit,
documented, tested configuration instead of a prose hardware blocker. This
is a routing/configuration change; it does not touch the deep byte-exact
decompilation track recorded under the other `g2-touch-*` audits (identity
recovery, relocated partition, per-unit admissions), which remains a
separate, still-open closure.

## What changed

### 1. Production routing

`g2/manifests/g2-2.2.6.10-touch-source-experimental.json` extends the base
release manifest (`g2-2.2.6.10.json`, the same pattern used by
`g2-2.2.6.10-codec-source-experimental.json` and
`g2-2.2.6.10-ring-source.json`) and overrides the `touch` component:

| Field | Before (base manifest) | After (this profile) |
| --- | --- | --- |
| `provider.kind` | `official_blob` | `source_build` |
| `provider.path` | `blobs/official/g2-2.2.6.10/firmware_touch.bin` | `build/touch-source-image/firmware_touch.bin` |
| `touch_application` region `address_status` | `inferred_from_vector_table` | `source_compiled` |

Every other component in the profile (codec, EM9305, case, Apollo
bootloader, Apollo main) is left untouched at `official_blob`; this item
routes only `touch`.

`make touch-source-experimental` builds the source image, then runs
`tools/open_cfw.py build` and `verify-artifacts` against the new manifest
profile and the narrow tests below. The assembled package is deterministic:
building it twice from the same providers produces byte-identical output
(`tests/test_touch_source_manifest_routing.py::test_manifest_verifies_and_assembles_deterministically`),
and its size/SHA-256 are pinned in the manifest
(`expected_size`/`expected_sha256`) the same way every other release
component is pinned.

The source image itself is materially smaller than the retained stock
`touch` payload it replaces (15,516-byte FWPK record / 15,484-byte raw
image, versus the stock blob's 34,464-byte FWPK record / 34,432-byte raw
image at flash `0x00000000..0x00008680`). This is expected and not a
completion gap: the source image is a from-scratch, protocol-compatible
clean-room reimplementation (see `runtime_touch_*` unit admissions), not a
byte-identical recompilation of the stock image, so a different size is the
normal outcome of not encoding stock bytes.

### 2. NVIC vector-slot configuration

`components/touch/source_image/psoc4000t_nvic.h` is new. It names every
PSoC 4000T Cortex-M0+ external IRQ (`OPEN_CFW_TOUCH_IRQ_IOSS0` ..
`OPEN_CFW_TOUCH_IRQ_TCPWM1`) with the NVIC IRQ number Infineon's public
`psoc4000t.svd` assigns it, in SVD order: IOSS0-4, SRSS_WDT, SCB0, SCB1,
MSCLP_LP, SPCIF, MSCLP, TCPWM0, TCPWM1 (13 external lines). This ordering
was already established, independent of any firmware byte, by
`g2-touch-identity-recovery.md` ("ARMv6-M vector-table shape", finding 4),
which cross-checked the *shape* of the shipped vector table (13 populated
external slots, all pointing at one default handler) against this public
SVD list to help identify the part. That finding does not read peripheral
assignment out of the firmware; the assignment is a fixed property of the
silicon, publicly documented, and knowable without a board or the stock
image.

Before this item, `components/touch/source_image/startup.c` encoded that
same, correct assignment (SCB1 = IRQ7, MSCLP_LP = IRQ8, MSCLP = IRQ10) as
bare positional entries in a 48-slot array, with a prose comment calling
the routing "evidence-locked pending board evidence." That conflated two
different things:

* **which IRQ number is SCB1/MSCLP** -- a silicon fact, public, and now
  named (`OPEN_CFW_TOUCH_VECTOR_INDEX(OPEN_CFW_TOUCH_IRQ_SCB1)`), pinned by
  `tests/test_runtime_touch_nvic_config.py` at both the header level (regex
  over the enum, no compiler) and the linked-ELF level (the named handler
  actually lands at that vector index, and every other external IRQ falls
  back to `Default_Handler`);
* **what MMIO behavior the handler body should perform on real hardware**
  (servicing the SCB1 I2C shift register, draining an MSCLP CapSense
  scan-complete result) -- this genuinely requires a physical part to
  develop and qualify against, and stays exactly as hardware-blocked as
  before. `SCB1_IRQHandler`, `MSCLP_LP_IRQHandler`, and `MSCLP_IRQHandler`
  are still empty ISRs; only their explanatory comments changed.

The vector table itself was also resized from the previous, unexplained
48-entry array (16 core + a generic 32-line Cortex-M0+ maximum) down to the
29 entries (16 core + the PSoC 4000T's actual 13 external lines) the
documented NVIC shape calls for, and rewritten with C99 designated
initializers keyed by the named IRQ so each populated slot states which
silicon interrupt it is instead of relying on position. This shrank the
raw image by 76 bytes (three fewer trailing vector words after alignment);
`tests/test_runtime_touch_nvic_config.py::test_vector_table_length_matches_documented_nvic_shape`
pins the linked array's ELF size to the documented shape so the two cannot
drift apart silently.

## What this item does not claim

* It does not add, remove, or reclassify any decompiled function in the
  byte-exact stock-image reconstruction tracked by the other `g2-touch-*`
  audits; that closure (per `g2-touch-software-readiness-ledger.md`) is
  unchanged by this item.
* It does not perform or authorize any hardware operation. `hardware_validation`
  stays `"blocked by unavailable physical evidence"` in both
  `touch-source-image-summary.json` and the manifest's component
  description.
* It does not claim the SCB1/MSCLP/flash-EEPROM/GPIO *runtime peripheral
  behavior* is qualified -- only that the *vector-slot assignment*, which
  is silicon configuration rather than behavior, is now explicit,
  documented, and tested instead of an unexplained blocker.

## Reproduction

```sh
cd g2
make touch-source-image           # builds the 31-TU source image + its own gate
make touch-source-experimental    # routes it via the manifest profile and verifies the package
python3 -m unittest tests.test_runtime_touch_nvic_config
python3 -m unittest tests.test_touch_source_manifest_routing
```
