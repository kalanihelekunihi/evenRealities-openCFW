# Authentic NationalChip DSP source rebuild: nine exact assembly bodies

**PASS: all nine selected bodies, totaling1,606bytes, reproduce byte-for-byte from authentic local assembly source.** Seven unchanged Apache-2.0 source files in the registered NationalChip lvp_kws checkout were preprocessed with installed Clang and assembled with the pinned official C-SKY binutils fork. There was one source/CPU/flag recipe, no flag sweep, no C implementation edits, retained blob/opcode arrays or normalized comparison.

This is genuine selected **assembly-source** reproducibility. It is not C-compilation, whole-archive/ELF reproducibility, firmware link equality, unique producing compiler identity or canonical admission.

## Exact bounded recipe and evidence

Source pin8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5, registered NationalChip lvp_kws. Files are under utility/libdsp, predominantly Source.asm, with bitreversal under Source. Per-file hashes, exact preprocessing/assembler commands, tool hash and all comparisons are in assembly-results.json. Authentic notices remain in the unchanged checkout. The SDK DSP Makefile explicitly lists the selected Source.asm transform/math/support paths; this existing KWS file is present, unlike the separate AIoT acquisition's missing referenced DSP Makefile.

Commands use Clang **only as the C preprocessor for assembler-with-cpp**, followed by target assembler `-mcpu=ck804ef -mhard-float -EL`. Clang does not generate C-SKY machine code. This recipe uses the SDK's supported target/AS settings. Original archived DWARF's GCC6.3/O2 C filenames were useful provenance, but not necessary to reproduce these assembly bodies and do not prove they were produced from current C counterparts.

| Rebuilt function | Complete matched code-section bytes |
|---|---:|
| csky_radix4_butterfly_q15 |530|
| csky_radix4_butterfly_inverse_q15 |530|
| csky_split_rfft_q15 |146|
| csky_split_rifft_q15 |86|
| csky_shift_q15 |116|
| csky_abs_max_q15 |76|
| csky_copy_q15 |44|
| csky_fill_q15 |40|
| csky_bitreversal_16 |38|

All nine comparisons use exact complete section lengths and SHA-256 against locked codec payload slices previously independently matched to archive bodies. There is no padding removal, relocation masking or caller-address rewriting. Extra sections emitted by the authentic files are not claimed reproduced unless separately tested. New object files and preprocessed assembly are retained here. The replay script requires a fresh output directory and source/assembler hashes; it never overwrites the sealed receipt. Example: `python reproduce.py --output /tmp/opencfw-dsp-fresh-replay` using the project venv Python with pyelftools. No redundant second execution was needed after the initial nine comparisons passed.

## Why this matters

The previously bound backup-codec512-point real FFT/inverse chain now has selected core/real-split/bitreversal/shift/copy/fill code that can be regenerated from licensed source, rather than relying on prebuilt archive bodies as source substitutes. This is a concrete reduction in selected rebuild uncertainty. It does not establish source for the private callers/GSC algorithm, aliases, startup selection, numerical equivalence for arbitrary inputs or full firmware behavior. The linked call/address/descriptor and2,272exact-table findings remain in the prior caller/table packet; no table-source compilation was performed here.

## C compiler availability and finite boundary

No executable matching C-SKY GCC6.3 distribution was located in the inspected documented OpenCFW environment/tool/recipe paths. The documented native GCC13 build recipe/pins exist, but its expected installed compiler is absent in this checkout; invoking a long unrelated compiler build would not test the producing6.3 candidate. Installed native C-SKY binutils suffices for every selected body above. Thus no new SDK/compiler download was needed to complete this finite selected assembly goal, and no C flag experiments were fabricated.

[Official NationalChip setup documentation](https://nationalchip.gitlab.io/ai_audio_docs/software/lvp/SDK%E5%BC%80%E5%8F%91%E6%8C%87%E5%8D%97/SDK%E5%BF%AB%E9%80%9F%E5%85%A5%E9%97%A8/%E6%90%AD%E5%BB%BA%E5%BC%80%E5%8F%91%E7%8E%AF%E5%A2%83/) names V3.10.15/B20190929/GCC6.3 and Linux x86_64/i386 or mingw bundles. Its public share returned a JavaScript portal shell; direct anonymous viewer metadata attempt returned404. These bounded receipts do not establish archive unavailability or private access requirements. No compiler archive/license was acquired, downloaded code executed, credentials supplied or authentication bypassed. Discovery separately verified the current official recommendation and retains its provenance; it is a candidate distribution, not proof of the stock producing checkout. Before a future C comparison, acquire/license-check the actual matching compiler and authenticate its binaries/host execution setup, plus selected C-source macros/headers and recipe. Do not reopen the exact nine-assembly result merely to perform a compiler hunt.

## Coverage / preservation handoff

New measurable result: **1,606bytes from nine sections have a successful authentic assembly-source replay recipe in analysis.** This improves source-rebuild evidence beyond object matching, but is not independently reviewed/admitted coverage yet. This packet creates no C-compilable percentage increase and no canonical stage/gate, build or coverage change. Old corpus completeness/freeze and whole-source/byte-equality claims remain separate. Full ELF/debug/link reproducibility is untested.

Prior receipts, source files, production, index, checkpoints,110inputs, firmware and devices are untouched. No commits, pushes, submodule changes, firmware/device/emulator execution or campaign admission. Independent review of this new rebuild recipe is the next useful validation; further numerics/alias/startup/private-code questions are separate goals.
