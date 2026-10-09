# Fresh provider evidence scan after the reviewed baseline

Two useful shortcuts emerged: **stock-byte-bound C-SKY DSP sources/debug metadata already inside the registered NationalChip SDK**, and **new pinned Pigweed HCI schemas with an authenticated Apollo packet-layout consumer**. The previous TDK/IOM6/BQ/flash findings are baseline, not new discoveries. This is an additive evidence audit, not a whole-firmware inventory-completeness certificate.

## Ranked findings and concrete next tests

| Rank | Finding | Evidence / confidence | Next bounded test |
|---|---|---|---|
| 1 | Existing NationalChip C-SKY DSP source and relocatable-object/DWARF shortcut | Nine unique exact nonrelocated code-section matches, **1,606 bytes**, in locked codec BINH B stage2; high confidence byte correspondence, producing SDK identity not unique. Newly verified in this pass, not a new SDK acquisition | Independently check the retained nine section hashes/offsets, then recover one forward/inverse Q15 FFT pair using its local source, DWARF types and constant tables; bind runtime placement/callers before assigning live algorithm roles |
| 2 | New Apache-2.0 Pigweed HCI Emboss schemas | Discovery's immutable pin e175383a07c5b811a98924fc662d1001f1d220d0; independent schema verification passes. This track freshly verified stock command/consumer hashes, literal and instructions. High protocol-layout confidence; no Pigweed firmware dependency claim | Trace readers of bitmap200714D8 to find actual mask decisions, or bind a frozen controller response; do not infer physical role capacity from schema/emulator fixture |
| 3 | Target C-SKY readelf for archived DWARF | Pyelftools default relocation handling rejects C-SKY relocation type1; pinned installed target readelf successfully resolves selected CU producer/source/type metadata. High confidence tooling behavior | Use this existing tool to export selected function/parameter/type metadata; do not silently parse unrelocated DWARF as resolved pointers or run a new compiler matrix |

## C-SKY DSP: new evidence inside a known provider

Registered NationalChip lvp_kws checkout HEAD is8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5. The `utility/libdsp` subtree contains381 C files and185 assembly files. Selected sources carry CMSIS/ARM Apache-2.0 and T-HEAD notices, explicitly describing arm→csky lineage in csky_abs_f32.c. These are source assets distinct from proprietary/prebuilt driver or speech/model algorithms; the root MIT label must not replace per-file notices.

A new bounded archive comparison checked only complete relocation-free `.text*` sections of16..4096 bytes against locked `firmware_codec.bin`:195 sections from libcsky_dsp.a,247 from libcsky_CK804ef_math.a, and3 from libvma.a. Eighteen archive hits collapse to **nine unique stock sections**, because two math archives contain identical bodies. No relocation masking, normalization, recompilation or source edits were used.

| Bound provider function | Codec package offset | Bytes |
|---|---|---:|
| csky_split_rfft_q15 | 0x47914 |146|
| csky_split_rifft_q15 | 0x479A8 |86|
| csky_shift_q15 | 0x47A00 |116|
| csky_abs_max_q15 | 0x47A74 |76|
| csky_copy_q15 | 0x47AC0 |44|
| csky_fill_q15 | 0x47AEC |40|
| csky_radix4_butterfly_q15 | 0x47D3C |530|
| csky_radix4_butterfly_inverse_q15 | 0x47F50 |530|
| csky_bitreversal_16 | 0x48164 |38|

Exact section/object/archive hashes and all duplicate hits are in dsp-object-evidence.json. Codec payload hash is recorded there. Existing canonical-image receipt identifies BINH B stage2 at component offsets[244032,326092), containing every listed match. These are package coordinates, not newly assigned CPU addresses. They do not prove the functions execute in any live audio path or that all stock DSP has source.

libcsky_dsp.a has322 ELF members,302 with debug sections. Target readelf metadata samples bind the matched FFT/shift objects to local source paths and recorded compiler `GNU C11 6.3.0 -mcpu=ck804ef -mfloat-abi=hard -g -O2 -fno-builtin -fstrict-volatile-bitfields -ffunction-sections -fdata-sections`. This is stronger per-object configuration evidence than a generic SDK Makefile. It does not transfer configuration to unrelated codec regions or uniquely identify a producing toolchain checkout. Source and DWARF metadata fingerprints are retained in source-provenance.json and dsp-dwarf-sample.json. The initial commentary's1,706-byte count was corrected by deduplicated accounting to1,606.

libvma.a yielded zero matches in the **three eligible relocation-free sections** checked. This narrow negative does not rule out VMA, GSC, relocated bodies or other archives. The retained stock source-path string lvp/vma/lavaliermic/gsc.c is consistent with a separate voice-processing region; no source binding or private DSP implementation is invented from that string.

## Pigweed schemas: independently checked stock relevance

Discovery acquired only hci_events.emb, hci_commands.emb, hci_common.emb and LICENSE, pinned at e175383a07c5b811a98924fc662d1001f1d220d0. The schema is a new protocol reference, not the producing Cordio or EM SDK. A full Pigweed/Emboss install is unnecessary for reading these layouts; schema compilation and generated-parser validation were not performed.

Fresh locked-byte review reproduces command producer HciLeReadSupStatesCmd `0x52B37C..0x52B396` (SHA f5157588cb8c13e2cce9404ff5ed7d6a6027954ae4ce6469f4050ad0ffce6dbd): opcode201C, parameter length0, conditional submit after allocation. Reset consumer `0x569B56..0x569D26` (SHA9749794a5293dc74c50f3595ac81c7d8a5c28a93cbe15c1ee155a1dda3ba077a) checks event0E, decodes LE opcode at event offsets3/4, advances source to offset6 and selects the arithmetic-switch201C branch at569C46. Summed opcode subtraction constants equal201C. That branch copies8bytes through439BE4 to destination literal569D44→200714D8. This agrees with schema status offset5 and bitmap6..13.

This selected routine skips status5 and contains no visible length guard. It does not establish absence of validation in upstream ingress or a confirmed malformed-packet bug. No stock mask decisions for bits6/35/41, actual bitmap values or EM controller response producer were established. Bit semantics are reference information only; emulator advertised values do not prove physical capacity. See hci-binding-independent-verification.json and fresh retained disassemblies. Discovery's detailed stock binding and the auditor's independent schema verification are pinned in input-references.json.

## Coverage, known families and ruled-out expansions

Read repository AGENTS/current workflow and emulator AGENTS. No .agents skill directory exists in OpenCFW; no applicable local skill was found. Emulator's explicit prohibition was honored. No emulator edits or further peripheral execution occurred. Discovery owns the emulator/source-comment pass; this track owns cross-component OpenCFW evidence review.

The current symbol inventory covers six component indexes: Apollo main8844 rows, bootloader292, codec778, BLE1835, touch298, case435. Module counts/hashes are retained in component-symbol-inventory.json. Unnamed/investigation rows are real gaps, not evidence of a new library. Printable source/compiler strings across the six payloads and consolidated registry/references were consulted as discovery aids; string absence is not provider absence. Previous reports keep Ambiq/Cordio, IAR/MetaWare, Infineon PDL/CapSense, ST HAL/Arm runtime, QP/C, NationalChip, libc/libgcc and registered utility families as known. None is presented as a new acquisition.

No new evidence justifies another full Zephyr, Ambiq, Nordic, Goodix, CMSIS or vendor SDK download. nPMX/TDK already have registered providers; known LC3 does not imply Opus/Speex/other host-tool codec dependencies are firmware-linked. VMA's narrow negative remains ambiguous. Shared CMSIS-style names would not suffice without the exact-byte/source evidence above.

The17:16 reviewed baseline remains authoritative for IOM6/GPIO, old TDK125-byte lineage, BQ whole-byte28 and conditional flash error path. No baseline audio tests, calibration scans or byte-match fixtures were repeated. No whole-firmware source-complete, unique producer, ROM-complete or global acquisition-exhaustion claim is made.

## Proposed references and remaining limits

Retain the four small Pigweed schema/reference files with Apache-2.0 notices/provenance; owner may consider a reference registration after review. Reuse existing NationalChip checkout's mixed-license DSP source/object metadata rather than adding a duplicate CMSIS SDK. Binary archives remain licensed reference/oracle inputs, not source substitutes for the byte-identical target. No registry update is applied.

New DSP matches need independent review and caller/runtime-coordinate binding before corpus claims. Pigweed still needs controller-response and actual consumer-policy evidence for hardware conclusions. Old CPU alias, vendor ARC arithmetic, private providers, unique case compiler configuration and whole-firmware P2 reconstruction boundaries remain distinct. All work is additive analysis; no campaign admission, canonical-ledger, production, index, Git or device mutation.
