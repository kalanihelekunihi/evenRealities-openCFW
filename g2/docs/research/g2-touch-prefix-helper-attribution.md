# G2 touch-prefix reachable-helper attribution

Status: all 44 generic helpers in the conservative shipped-prefix call closure
now have typed behavior/provider boundaries. Historical source commits and
private symbol tables remain unavailable and are not claimed.

## Method

`tools/analyze_g2_touch_prefix_helper_evidence.py` consumes the authenticated
63-entry prefix map and requires its pinned row digest
`335e09b1d61057a49e69d4f58f9e9117f4e8db4f475068f76ba3f544919a5e7a`.
For each of the 44 rows previously named `touch_sub_*`, it records:

- exact reachable instruction digest and byte count;
- callers and direct callees;
- PC-relative SRAM, MMIO, resident, and status-code literals;
- a behavior/provider boundary;
- a proposed clean-room or public-provider name with an explicit name-status
  level;
- the implementation license rule for that boundary.

The analyzer requires the typed-entry set to equal the generic-entry set. A new
or removed generic helper fails rather than silently falling through.

## Result

| Boundary | Helpers | Disposition |
|---|---:|---|
| OpenCFW clean-room application policy | 8 | independently implement under MIT |
| Infineon CAT2 PDL / CMSIS-facing helpers | 10 | prefer upstream Apache-2.0 provider code and notices |
| Infineon CAPSENSE middleware | 3 | EULA source is evidence only; use an MIT clean-room replacement unless its terms are accepted |
| Infineon Emulated EEPROM middleware | 16 | EULA source is evidence only; use an MIT clean-room replacement unless its terms are accepted |
| ARM EABI / C runtime | 7 | link the selected toolchain/libc provider under that provider's license |

The deterministic evidence digest is
`27b3373ad1475a6370eb0acb338f4564e10ba523a4e35d10ab6f61406b00329d`.
Thirty-five boundaries are high confidence and nine are medium confidence.
There are no remaining untyped helpers in this 44-entry reachable tranche.

“No remaining untyped helpers” does not mean that every historical symbol is
known. It means every helper has an actionable implementation boundary. No
historical generating commit or private symbol is asserted.

## Public provider matches

The public provider references are pinned in
`tools/manifests/g2-touch-prefix-provider-boundaries.tsv`:

- Infineon `mtb-pdl-cat2` commit
  `35f1714623cfea682d5e285af80d50416b4c7bbc`, Apache-2.0;
- Infineon `capsense` commit
  `b68b744eb75fe976fc5ddd7b16e04e1a5a54bdd3`, Infineon EULA;
- Infineon `emeeprom` commit
  `6bbde322b7193528674dbf7fcdc2e971d0cff4fa`, Infineon EULA.

These commits are comparison anchors, not claims that the official binary was
built from those revisions.

### CAT2 PDL island

Six helpers have strong public-interface matches:

- `0x1180` — `Cy_SysLib_DelayCycles`; its complete 18-byte body follows the
  public CM0+ assembly sequence: add two, divide cycles by four, add/sub loop,
  two alignment NOPs, return;
- `0x65F4` — `Cy_SCB_I2C_Init`; three-argument base/config/context ABI, SCB
  register initialization, input assertions, context clearing, and status
  return;
- `0x6F14` — `NVIC_SetPriority`; signed core/external IRQ mapping over
  `0xE000ED00` and `0xE000E100`;
- `0x6F74` — `Cy_SysInt_SetVector`; SRAM-vector selection and previous-vector
  return;
- `0x6FA8` — `Cy_SysInt_Init`; priority plus conditional vector installation;
- `0x6FF0` — `Cy_SysLib_Delay`; overflow-bounded millisecond chunks followed by
  `milliseconds * cy_delayFreqKhz` delay cycles.

The MSCLP register preparation/write/wait helpers and timeout scaler are typed
as CAT2 PDL candidates. Their register and caller topology is strong, but the
exact public symbol names are not promoted without an exact version match.

### Emulated EEPROM island

The `0x4B68` helper implements CRC-8 with seed `0xFF`, polynomial `0x31`, and
eight MSB-first rounds. Those constants and operations match the public
Emulated EEPROM `CalcChecksum` contract. The same cluster carries the complete
`0x093E0000` through `0x093E0004` status family and a coherent row-integrity,
sequence-number, wear-level, redundant-copy, simple-read, and extended-read
call graph.

Strong symbol/behavior matches include `CalcChecksum`,
`CalculateRowChecksum`, `GetStoredRowChecksum`, `CheckRowChecksum`,
`GetStoredSeqNum`, `GetNextRowPointer`, `GetReadRowPointer`, and
`Cy_Em_EEPROM_Read`. Other private helpers are marked candidates or given a
typed `em_eeprom_*` name; physical order alone is never used as proof.

The public `emeeprom` repository is not MIT or Apache-2.0. It carries the
Infineon EULA, so this analysis does not authorize copying that implementation
into an MIT file. Its API, constants, and call topology are used to define a
clean-room boundary.

### Runtime island

The ABI/behavior is exact for:

- `0x73C0` `__aeabi_uidiv`;
- `0x74CC` `__aeabi_uidivmod`;
- `0x74D4` `__aeabi_idiv`;
- `0x76A0` `__aeabi_idivmod`;
- `0x76A8` `__aeabi_idiv0`;
- `0x76D4` `memset`;
- `0x772C` `memcpy`.

The exact historical compiler/libc provider is still unavailable. OpenCFW
should link the chosen upstream runtime under its own license rather than copy
the official bytes or guess a license.

## Clean-room application-policy boundary

Eight functions are typed from the existing config/report/sensing evidence:
config read and load adapters, saved-baseline read/update, attention timeout
rearm, a zero-timeout default, and the gesture state-machine island. Proposed
names in this class describe observed behavior and are intentionally not
historical symbol claims. New implementations may be project-authored under
MIT.

## Artifacts and verification

- `tools/analyze_g2_touch_prefix_helper_evidence.py` — MIT analyzer;
- `tools/manifests/g2-touch-prefix-helper-evidence.tsv` — all 44 helper rows;
- `tools/manifests/g2-touch-prefix-provider-boundaries.tsv` — provider commits,
  licenses, and implementation rules;
- `tools/manifests/g2-touch-prefix-helper-evidence-summary.json` — counts,
  clean-room rules, and remaining-opacity statement;
- `tests/test_analyze_g2_touch_prefix_helper_evidence.py` — boundary coverage,
  provider/license, register/status, runtime-name, and deterministic-output
  tests.

Run:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 \
  g2/tools/analyze_g2_touch_prefix_helper_evidence.py --write-manifests
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  g2/tests/test_analyze_g2_touch_prefix_helper_evidence.py -v
```

This work is offline analysis only. It performs no device access, reset, DFU,
flash, timing measurement, or electrical test, and makes no physical behavior
or release-fitness claim.
