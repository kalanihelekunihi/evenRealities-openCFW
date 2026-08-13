# Generic device-registry ownership boundary

## Result

Nine recovered functions implement the stock name-based device registry and its operation-table
dispatch. Their subsystem semantics are clear, but no attributable upstream project, vendor
version, or license has been established. They are therefore recorded as
`unknown_generic_device_registry_candidate` with disposition
`investigate_before_implementing`, not as R1-owned code.

openR1 does not reproduce this framework. Product adapters bind directly to admitted Nordic,
Bosch, ST, FlashDB/FAL, or abstract licensed-provider interfaces. This preserves required device
behavior without silently treating an unidentified framework as clean-room product code.

Six fixed two-wire record-binding wrappers are separately admitted as R1 configuration, not as
registry implementation. Their exact extents and direct-typed-binding replacement are documented
in [`BUS-REGISTRATION-CORRELATION.md`](../correlation/BUS-REGISTRATION-CORRELATION.md).
The four associated GPIO-driven bus engines are a distinct forty-function unidentified-provider
boundary. Their recovered behavior does not authorize reconstructing the registry or engine; see
[`SOFTWARE-TWI-PROVIDER-BOUNDARY.md`](SOFTWARE-TWI-PROVIDER-BOUNDARY.md).
One additional fixed RTC record-binding wrapper is admitted under the same configuration-only
rule, while its seven generic RTC-device operations remain separately source-gated; see
[`RTC-DEVICE-PROVIDER-BOUNDARY.md`](RTC-DEVICE-PROVIDER-BOUNDARY.md).

## Recovered layout

A registry record contains at least:

| Offset | Recovered role |
| ---: | --- |
| `0x00` | non-null device name |
| `0x04` | non-null operation-table pointer |
| `0x14` | next registry record |

`0x00085D58` rejects null records, duplicate names, missing names, or missing operation tables. It
appends a valid record to a global singly linked list, clears the record's next pointer, and returns
one on success. `0x00085CE0` walks the same list, compares the requested name against offset zero,
and returns the matching record or null.

Seven dispatchers validate the record, load its operation table from offset `0x04`, and invoke a
slot only when that slot is non-null. A null record returns `1`; a missing operation returns the
slot-specific status shown below. Arguments and return values are passed through to the selected
provider operation.

| Extent | Operation-table slot | Missing-operation status |
| --- | ---: | ---: |
| `0x00085D08..<0x00085D1A` | `0x00` | `5` |
| `0x00085D1A..<0x00085D2C` | `0x08` | `5` |
| `0x00085CBA..<0x00085CCC` | `0x0C` | `6` |
| `0x00085D2C..<0x00085D46` | `0x10` | `2` |
| `0x00085DA8..<0x00085DC2` | `0x14` | `3` |
| `0x00085CCC..<0x00085CDE` | `0x18` | `7` |
| `0x00085D46..<0x00085D58` | `0x20` | `9` |

The slot names are intentionally not guessed. Callers establish that the table is shared across
named ADC, bus, flash, motion, NFC, PMIC, and touch records, but caller use alone does not identify
the framework's author.

## Clean replacement policy

- Nordic SDK APIs own nRF52840 drivers and hardware primitives.
- Attributable Bosch, ST, FlashDB/FAL, tiny-AES, and other admitted sources own their respective
  provider implementations.
- R1-local code may contain only fixed product configuration, bounds, state policy, and narrow
  adapter glue already admitted in the ownership ledger.
- Proprietary or unidentified device operations remain behind disabled semantic provider
  interfaces until licensed source is supplied.
- The linked Nordic target must not acquire a clone of this global registry merely to match stock
  architecture; direct typed bindings are the cleaner functional equivalent.

This boundary does not authorize any signing, rollback, protection, diagnostic, or deployment
bypass.
