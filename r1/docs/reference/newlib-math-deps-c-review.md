# Pinned newlib math dependencies for firmware diagnostics

The normal R1 application composition now includes the unchanged newlib 3.3.0
s_fpclassify.c and s_frexp.c providers from the already-pinned upstream tree.
They close __fpclassifyd and frexp, which the selected vfprintf requires.
The source pin is commit 6d79e0a58866548f435527798fbd4a6849d05bc7; existing
license notices and source bytes are preserved. No precompiled libm archive
or proprietary compiler is introduced.

The final probe links the normal participating source objects with garbage
collection and no unresolved references. It executes both providers, their
existing C double-multiply dependency and a normal hard-float C caller. No
stock code is mapped and no providers are modeled. An independent integer-bit
oracle checks classification, returned mantissa bits and the written exponent
for 21504 patterns: both signs, every binary64 exponent, five selected
mantissas and 1024 seeded arbitrary words. Zero signs, subnormals, infinities
and NaN payloads are included. The exponent buffer is guarded; classification
must not write it. Eight combined C-caller cases verify the ABI. All 43016
calls pass, with saved core/VFP registers, SP and interrupt masks checked.

Four compiled defects are detected: normal classified as zero, subnormal
classified as normal, wrong initial exponent and wrong subnormal exponent
adjustment. A clean final baseline runs afterward. Tests use the default FP
environment only; they do not establish exception flags, arbitrary rounding
modes, complete vfprintf decimal formatting or physical hardware behavior.
The remaining formatter allocation, locale, dtoa and output dependencies are
not hidden or stubbed in the normal composition.

An audit finds 784 unchanged prior object hashes. The two generated bootloader
objects differ in metadata but retain allocated bytes and relocations. The
two upstream provider units are the only additions. R1 compiles 788 units
(706 application, 82 bootloader), without failures or duplicate strong symbols.
Application imports fall from 105 to 103 with none added. Bootloader metadata
imports remain 22 and strict source bootloader linking succeeds. Global source
checking retains the unrelated unlisted G2 resident_rom_thumb_set.S failure.
No source-plan qualification is added; full application linking is unfinished.

A separate Bosch callback experiment was discarded before this final build.
The native read path deliberately loads the callback slot as a full-word
function and forwards full register words; replacing registration aliases
with narrower SDK callbacks would weaken that native contract. The original
native_bma_interface.c source and object hashes match the preceding accepted
build. No Bosch registration change is part of this result.
