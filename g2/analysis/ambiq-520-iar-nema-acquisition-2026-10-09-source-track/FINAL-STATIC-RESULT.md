# Authenticated IAR Nema candidate: bounded static result

This additive result supersedes the earlier relocation and PDF-extraction limitations in this directory. It does not change canonical ledgers or symbol confidence.

## Acquisition and provenance

The user-supplied `AmbiqSuite_5.2.0.zip` is 907382158 bytes, SHA-256 `d9751350ef593b306838792a64a5620e4912c84ddf32dc9ff6aacd5cca049cad`. All 30485 ZIP members passed CRC validation. Release notes identify `release_sdk5p2p0_66487dd10`, July 24, 2026.

The isolated Apollo510 IAR archive at `extracted/third_party/ThinkSi/config/apollo510_nemagfx/iar/bin/lib_nema_apollo510_nemagfx.a` has SHA-256 `8c6204496ab53860241db9236487a0eb93badf9627be4eea55249847813827e7`. Its `nema_cmdlist.o` member has SHA-256 `2bbb07808e3e2aca417829dc3edc9a6e78d17c8df69fdce3341088af5e7c2e70`. Embedded producer strings identify IAR ARM 9.70.1.475/W64. This does not identify the stock compiler version.

## Complete named-function comparison

Historical provenance names locked stock `0x5143D4..0x5144BA` as `nema_cl_bind_sectored_circular`; the canonical seed remains Unverified. The complete stock extent is 230 bytes, SHA-256 `1b72806af461fbd44dc0a8928e9a4b4493d124242f8f89f7d5820d0c8c692b6d`. The reference package SHA-256 is `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.

The candidate symbol is Thumb-valued 885, instruction offset 884 (`.text+0x374`), size 222, in the complete 5644-byte shared text section. Candidate function SHA-256 is `e8b0d7c0bc4363c4f2d266fced1ff65764b59e4ec84346ffd8570f191616ddca`; full text SHA-256 is `51f3b98557d957b556c2bdb4629e1807170dfee35d9cb04d629aaeaa91199153`.

All three function relocations are enumerated and explicitly encoded in `RELOCATION-CLOSURE.json`, without masking or truncating text:

| Candidate offset | Relocation | Explicit stock-derived binding | Encoded bytes |
|---|---|---|---|
| +110 | R_ARM_THM_JUMP24 | P=0x514442, S=0x4B127C, addend=-4 | 9cf71bbf |
| +114 | R_ARM_THM_PC12 | P=0x514446, aligned PC=0x514448, literal=0x514B78, displacement=0x730 | dff83067 |
| +172 | R_ARM_THM_CALL | P=0x514480, S=0x4B127C, addend=-4 | 9cf7fcfe |

The literal table itself carries R_ARM_ABS32 against `nema_context`, addend zero; the corresponding stock cell contains `0x20074EFC`. The candidate target names are inferred bindings from agreeing stock branch/literal sites, not independently closed global-symbol identities. The third stock call is at `0x514488`, eight bytes later than the straight candidate placement; its different encoded displacement reflects that shift.

Stock contains this additional executable block at `0x514476`:

```
ldr   r2,[r0,#24]
bic.w r2,r2,#32
str   r2,[r0,#24]
```

At the corresponding candidate point (`.text+0x416`) execution proceeds directly to `movs r0,#0`. Stock therefore clears flags bit 5 and the candidate does not. The eight bytes are internal semantic instructions, not trailing padding; stock's final eight bytes are executable epilogue instructions. The internal branch targets and remaining tail reflect the insertion.

The explicitly patched 222-byte candidate SHA-256 is `40a8179d46fc3b662501879fcb79f79c3ffe5fb2336c6c09d52f1eff64649261`; complete equality to the 230-byte stock extent is false. This excludes this specific candidate function as an exact text producer. It does not exclude the entire SDK, identify the exact stock source revision, or establish whole-program linking. IAR linker relaxation was not simulated; ordinary relocation resolution cannot supply the missing flags update.

## License review and limits

Trusted macOS PDFKit extracted both supplied license PDFs without a password or bypass; extracted text is retained here. The previous AES-backend extraction limitation is closed. The top-level BSD terms defer third-party terms. ThinkSi's permissive notice expressly covers headers and associated documentation; it does not establish a permissive grant for this binary archive. The Ambiq PDF terms include evaluation/chip-use conditions and restrictions on translation, reverse engineering, decompilation and disassembly, subject to applicable-law exceptions. No new agreement was accepted, and no unrestricted binary-analysis or redistribution permission is certified by this report.

Inspection used trusted static tools, with no downloaded SDK code execution. No firmware sources, canonical ledgers, root index, submodules, device state or seals were changed by this comparison. No proprietary-binary submodule addition is proposed. Full legal scope, independently named relocation globals, and exact stock producer provenance remain unresolved.
