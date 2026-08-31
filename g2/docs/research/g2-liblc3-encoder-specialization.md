# G2 Apollo liblc3 encoder specialization experiment

Status date: 2026-08-30  
Target: official G2 `s200_v2.2.6.10` Apollo-main image  
Result: one evidence-safe reduction found; current authenticated headroom still
missed by 30,516 bytes

## Configuration evidence

The firmware does not statically disclose one exact LC3 configuration. Four
authenticated service contexts occupy consecutive 2,628-byte SRAM slots:

| Context | Header | Encoder storage |
|---:|---:|---:|
| `0x20106A7C` | 28 bytes | 2,600 bytes |
| `0x201074C0` | 28 bytes | 2,600 bytes |
| `0x20107F04` | 28 bytes | 2,600 bytes |
| `0x20108948` | 28 bytes | 2,600 bytes |

The first, second, and third pointers are authenticated through the table at
`0x0058F880`; the fourth occurs in the independent literal cells at
`0x0054F9A0` and `0x0057B3E4`. The next allocation starts exactly one slot
later at `0x2010938C`.

Recovered `service_audio` code reads these header fields at encode time:

| Offset | Field | Static value available? |
|---:|---|---|
| `0x00` | PCM format | No |
| `0x04` | frame duration in microseconds | No |
| `0x08` | encoded sample rate | No |
| `0x0C` | channels/PCM stride | No |
| `0x10` | interleaved channel offset | No |
| `0x14` | bitrate | No |
| `0x18` | cached encoder pointer | Runtime state |
| `0x1C` | encoder storage | Fixed slot extent |

The source boundary previously authenticated by the PT analyzer explicitly
classifies initialization as `runtime-provided; statically unproven`. The five
LC3 callsites load duration, rate, bitrate, format, and stride from those
headers rather than immediate constants. Therefore no exact duration, non-HR
sample-rate subset, bitrate, or PCM-format subset can be promoted from the
official bytes.

Two properties are exact:

- the service calls only the public non-HR LC3 API, whose wrappers pass
  `hrmode=false`; and
- setup passes `sr_pcm_hz=0`, which liblc3 normalizes to the encoded sample
  rate.

This permits disabling LC3-Plus HR while retaining all four non-HR durations,
all five non-HR sample rates, dynamic bitrate/stride, and all four PCM loaders.
It does not permit fixing any of those remaining values.

## Deterministic build result

`build_specialization_experiment.py` compiles the same pristine v1.1.3-era
source snapshot, provider, Cortex-M55 profile, roots, and section-GC contract
as the baseline component. It adds only `-DLC3_PLUS_HR=0`; no upstream file is
modified. Its LC3-specific linker policy names the five logically immutable
pointer objects `.lc3_table_rodata` and authenticates the post-link read-only
conversion.

| Section | Baseline | Non-HR-only | Reduction |
|---|---:|---:|---:|
| text | 43,248 | 40,880 | 2,368 |
| rodata | 85,088 | 60,316 | 24,772 |
| table rodata | 404 | 404 | 0 |
| raw total | 128,740 | 101,600 | 27,140 |
| aligned span | 128,752 | 101,616 | 27,136 |

The admitted post-policy relocatable object is 116,268 bytes, SHA-256
`bc548b0578f87d43c38def5fb727533a73d7e2f31105e5e8bd0d0a1fef336b7d`.
It retains 484 relocations and 11 runtime imports; `roundf` disappears with the
HR-only code. Text, rodata, and table-rodata hashes are pinned in
`specialization_experiment.json`.

The current core still supplies only 71,100 append bytes. The admissible
101,616-byte aligned span ends at `0x00805734`, leaving a **30,516-byte
shortfall** beyond the protected `0x007FE000` update record. The safe reduction
closes 27,136 of the original 57,652-byte gap but does not authorize placement.

Host qualification builds the pristine baseline and the non-HR specialization
side-by-side, then compares provider plans and encoded bytes for all 80
duration/rate/PCM-format combinations (four durations, five rates, four
formats), plus a bitrate grid. All compared outputs are identical. This is
software evidence only, not acoustic, WCET, stack, BLE, or device evidence.

## Rejected counterfactual

For measurement only, the experiment also builds
`-DLC3_PLUS_HR=0 -DLC3_PLUS=0`. That removes 2.5 ms and 5 ms support, so it is
explicitly evidence-rejected because `frame_us` is runtime-provided. It would
reduce the aligned span to 92,176 bytes, but would still miss authenticated
headroom by 21,076 bytes. Thus even the unsupported duration assumption does
not solve placement.

Sample-rate table pruning would require a source specialization and proof that
runtime `sample_rate_hz` cannot select the removed rows. PCM-loader pruning
would require equivalent proof for the runtime format field. Bitrate is
dynamic and shares the core entropy/SNS/TNS/spectral tables rather than owning
a separable per-bitrate table family. None of these reductions is attempted or
credited.

Production routing remains blocked. The builder proves its finalization path
at explicitly synthetic addresses: all 484 input relocations are applied, all
78 initialized table words are checked, and XIP bytes are emitted only after
the final ELF is relocation-free. Those test addresses and runtime bindings
carry no stock authority. The experiment assigns no production address,
patches no service call, emits no OTA image, and does not supersede the
existing LTPF route.

## Reproduction

```sh
python3 g2/tools/analyze_g2_liblc3_encoder_specialization.py --pretty
python3 g2/components/apollo_main/liblc3_encoder/build_specialization_experiment.py
python3 -m unittest -v g2.tests.test_apollo_liblc3_encoder_specialization
python3 -m unittest -v g2.tests.test_apollo_liblc3_specialized_xip
```
