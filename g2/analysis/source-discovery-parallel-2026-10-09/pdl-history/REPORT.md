# Official PDL Configure source-history discriminator

## Result

No distinct published **loop implementation** or loop-count configuration was found that explains the existing 24-byte GNU 13.3 mismatch in Configure `[0x8FD0,0x9178)`. Official history contains three textual Configure variants; the variants differ only by trim-frequency identifiers and whitespace. Both register-copy loops are identical throughout. Device loop counts stay 8 global functions and 3 sense modes in every historical PSoC4000T configuration change examined.

This is a bounded negative result for the official public history, not a claim that private sources, patches, translation-unit environments or other compiler settings cannot explain the target. No compile experiment was performed.

## Official acquisition and exact revision inventory

Remote verified anonymously: https://github.com/Infineon/mtb-pdl-cat2.git . A bare partial clone is isolated at `../acquisitions/infineon-pdl-history.git`; its refs pin published commits. `history-inventory.json` records all public tags and path-specific change commits. `receipts.json` records acquired source/header/release/license file hashes and Git object identities where recorded. Sources retain Apache-2.0 notices. The registered canonical PDL directory is uninitialized and has no local `.git`; querying `git -C` there resolves the root repository, so its root HEAD/origin must not be described as the PDL pin. Existing authenticated /tmp PDL source and owner report were read without mutation.

| Candidate official revision | Role / exact Configure delta |
|---|---|
| `69bb46becb33da0215576d6d22f6b225165d4c28` (release-v2.0.0-Beta1) | earliest published MSCLP; old 24/36/48 MHz names and one whitespace difference |
| `1ec034466fc674c1b165c03fabe3a661d04860e5` (release-v2.0.0) | old 24/36/48 MHz names; current loop text |
| `a4ab2c8bf8e84b4f421e19b2d9580bb72ae174ac` (release-v2.3.0-Beta2) | current 25/38/46 MHz names; current Configure body |
| `db8ea6270ce8c66ca04f00ee61fa6e7e76dd31c3` (release-v2.5.0) | source-file changes elsewhere; Configure body unchanged |
| `84b493b1fb8105735f157fe3570ef940b3a277ca` (release-v2.20.0) | source-file changes elsewhere; Configure body unchanged |
| `35f1714623cfea682d5e285af80d50416b4c7bbc` (release-v2.21.0, existing canonical pin) | source file identical to 2.20; baseline receipt SHA-256 `2613ec6fee3ac2ca6d8a42e483bb671f9ed63a58045b125ee6fe11f6f2d60f07` |

Full-source path history has only five change commits: Beta1, 2.0.0, 2.3.0-Beta2, 2.5.0, 2.20.0. All tagged source-blob identities are recorded to avoid duplicate builds of unchanged variants. `configure-versions.json` binds extracted bodies to exact source lines/hashes; every extraction has a diff versus 2.21.

## Exact source and macro deltas

Baseline `drivers/source/cy_msclp.c:347–350` copies `SW_SEL_CSW_FUNC[index]` with uint32 index and `< MSCLP_CSW_GLOBAL_FUNC_NR`. Lines 353–362 copy seven mode fields with `< MSCLP_SENSE_MODE_NR`. No conditional macro changes either loop within Configure; only file-wide `CY_IP_M0S8MSCV3LP` enable gate applies. The function has no `CY_ASSERT`, inline wrapper, restrict qualifier or per-function optimization pragma in any acquired body.

The old/current function delta is at baseline lines 366–383: CY_MSCLP_IMO_{24,36,48}_MHZ changes to {25,38,46}_MHZ, along with associated SFLASH macro names. Header enum macros remain numerically **0,3,6** (`drivers/include/cy_msclp.h`), respectively. `cy_device.h` trim access remains a cast to uint32 of an SFLASH struct field; exact old/new macro extracts are acquired at lines 100–105 (2.0.0) and 203–208 (2.21). This nominal frequency rename is not an alternate copy-loop algorithm.

All historical changes to `devices/include/psoc4000t_config.h` examined retain **MSCLP_SENSE_MODE_NR=3u** and **MSCLP_CSW_GLOBAL_FUNC_NR=8u**. Baseline locations are lines 579 and 594. Hardware arrays remain MODE[4] and SW_SEL_CSW_FUNC[8] (`cyip_msclp.h:144,149`), distinct from the selected loop count 3. Driver configuration maximums remain 4 and 8 (`cy_msclp.h:447,449`). Confusing hardware/structure maximum 4 with device-used count 3 would change behavior and is not an official historical explanation.

MSCLP_MODE_Type normalized declarations are unchanged across all official header change commits. Full MSCLP_Type changes once between early 2.0.0 and 2.2/2.3 headers: STATUS4 is inserted at 0x140C, following status/FIFO fields shift, reserved padding shrinks to keep FRAME_CMD at 0x1800. Configure does not access that status block; its MODE and switch-control offsets/types remain unchanged. Subsequent normalized declarations stay the same. Other IP bitmask changes exist but are not referenced by the mismatched copy loops. Full historical headers and `header-constraints.json` preserve the evidence rather than implying all IP revisions are identical.

## Official supported environments versus producer identity

Release documentation gives tested software/tool versions, not the original G2 producing compiler. Examples: Beta1 GCC10.3.1/IAR8.42.2/Arm6.13; 2.0.0 and 2.3-Beta2 GCC10.3.1/IAR9.30.1/Arm6.16; 2.5 GCC11.3.1; current 2.21 GCC14.2.1/IAR9.50.2/Arm6.22/CMSIS-Core6.1/core-lib1.7.0. README requires core-lib >=1.1.4. Current baseline tested macros and original-generated configuration remain owner evidence, separate from release support tables.

Official documentation entry: https://infineon.github.io/mtb-pdl-cat2/pdl_api_reference_manual/html/group__group__msclp.html ; release notes are pinned locally for the above versions. No documentation supplies a alternate loop syntax, device-dependent loop count beyond the acquired headers, or original translation-unit setting for this target.

## Bounded owner candidates and stopping boundary

1. Reconcile exact preprocessed Configure tokens, device header selection, `__IOM` volatile expansion, MSCLP/config type declarations and uint32 definition from the producer environment against the preserved baseline. These are translation-unit candidates, not discovered official alternatives. Full source has ordinary nonvolatile config reads and volatile MMIO writes; inserting restrict/volatile or changing index type would be a speculative source experiment, not an upstream revision attribution.
2. If testing historical versions, use only the early 2.0.0 family as a genuinely different naming/IP-header candidate; 2.3-Beta2 through 2.21 Configure bodies are identical and do not warrant redundant source-version compilation. Early loop text/counts still do not explain a loop-only mismatch by themselves.
3. Supported GCC14.2.1 is documented but was not acquired or compiled here. Testing it is the owner's compiler-discrimination decision; release support does not establish G2 used it. Existing 10.3/11.3/12.2/13.3 results are not rerun.

No useful new Configure submodule is proposed: current registered PDL already covers the body, and isolated historical file receipts suffice for owner experiments. No canonical source, root .gitmodules/index, existing evidence, Docker/device state or authenticated inputs were changed. Missing private translation-unit/compiler environment remains unresolved.
