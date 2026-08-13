# G2 nPMX main-driver recovery and exact public-source candidate

Status: authenticated linked-object closure and exact public upstream candidate
for official G2 `2.2.6.10`. No hardware or flash operation was performed.

## Result

The stock retained path
`driver\npmx_driver_transplant\src\npmx_main_driver.c` is a first-party
integration wrapper around Nordic Semiconductor's BSD-3-Clause `npmx` PMIC
library. Its eleven retained-path anchors / 2,290 bytes expand to thirty linked
functions / 6,560 body bytes. The complete physical wrapper object is
`[0x00511002,0x00512BC0)`, 7,102 bytes.

The wrapper makes 72 direct calls to 42 linked nPMX entries. Those entries map
to the generic backend plus nPMX core, ADC, charger, timer, VBUS input, buck,
load-switch, and ship-control APIs. The other 331 external calls close at
EasyLogger (310), CMSIS-FreeRTOS tick access (2), IAR DLIB (2), first-party I2C
and delay providers (9), and a first-party orientation/calibration seam (8).
No third-party implementation is copied into the wrapper object.

## Origin, version, and commit

The origin is the official
[`NordicSemiconductor/npmx`](https://github.com/NordicSemiconductor/npmx)
repository. Stock selects the unique public state
`e1aaec53f456887a7d7b80d82f684d1ac3cb08c8`, described by Git as
`v1.0.1-1-ge1aaec5`:

| boundary | official commit | stock evidence |
|---|---|---|
| lower / included | `e1aaec53…`, 2025-02-12, “fix and simplify usage of result registers” | linked `npmx_adc_meas_all_get` reads the ten-register result bank and uses separate MSB/LSB offset logic introduced by this commit |
| upper / excluded | adjacent `53de7af4…`, 2025-04-14, “Fix float promotion” | linked `npmx_common_ln_get` retains three `vcvt.f64.f32`, four `vmla.f64`, one `vcvt.f32.f64`, and the five exact upstream double constants; the next commit changes these expressions to `float` |

The commits are adjacent in official history. The paired positive and negative
fingerprints therefore identify `e1aaec53…` exactly among public upstream
commits. The stock timestamp `2025-04-28T13:29:15Z` is consistent with that
selection and predates Nordic's May 9 nPM1304 commit. A private fork or
cherry-pick producing identical source remains unprovable from the binary, so
this is an exact **public source candidate**, not a claim about Even's private
Git object.

The byte-identical compact snapshot under `third_party/npmx` admits all driver
sources and headers, the backend, root API headers, templates, license, and
release metadata from tree `87fb8b8e3e1068736cd2c02526442e03e67c381c`.
The generated 502-KiB nPM1300 ADK is deliberately deferred until production
integration needs it.

## Object evidence

The fail-closed audit pins 2,281 reachable instructions, 420 direct calls, 35
whole-image BL entry sites, four stored function-entry pointers, 62 literal
references through the three retained-path cells, and no indirect call,
strict-interior ingress, or non-code BL ingress. Body SHA-256 is
`3d0d625389b666d0678a9647142cc51f73b6f26c399cc1fbc4e1b1aeaad3c0ff`;
physical SHA-256 is
`a6e4c6d368d0ebd48f6821294b2f9d78462eb3b90748208ea2462c8623145895`.

Production routing remains intentionally false. The admitted upstream source
shortcuts PMIC implementation work, but OpenCFW still needs a reviewed nPM1300
ADK/configuration, Apollo510 I2C backend, interrupt wiring, and the G2-specific
rail/charger/orientation policy before the driver can safely control hardware.

## Reproduction

```sh
python3 third_party/npmx/verify_snapshot.py
make npmx-main-driver-closure
```

Evidence is pinned in:

- `tools/manifests/g2-npmx-main-driver-function-map.tsv`;
- `tools/manifests/g2-npmx-main-driver-provider-map.tsv`;
- `tools/manifests/g2-npmx-main-driver-closure.tsv`; and
- `third_party/npmx/PROVENANCE.json`.
