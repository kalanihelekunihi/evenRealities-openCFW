# Independent NationalChip DSP object-match audit

Reviewed owner [report](../fresh-provider-evidence-audit-20261009T192906Z/REPORT.md), [completion](../fresh-provider-evidence-audit-20261009T192906Z/completion/SUMMARY.md), archive match ledger and source/DWARF records. [Bounded independent verification](DSP-INDEPENDENT-VERIFICATION.json) passes37 checks; [reproducible checker](verify_dsp.py) parses retained ar/ELF32 inputs directly and invokes existing target readelf only for metadata. No firmware/object execution, source compilation, downloads, Git/index/source/campaign/device changes.

## Nine matches accepted

Independent unmodified ELFsection→lockedfirmware comparison confirms all18 recorded archive hits, every complete section hash/size and every unique package occurrence. Deduplication by(stockoffset,length,sectionhash) yields9nonoverlapping spans and1606bytes. Whole codec payload SHA b06dfef7faa2f1e52d2aacd07958d4b96ffc36dca5077ac9149e48f19fc9c4d0 and all three archive hashes/member counts agree. Matched section flags include executable; relocation sections of typeREL/RELA targeting each matched section contain zero entries. Debug relocations elsewhere do not invalidate text equality, but are relevant to DWARF interpretation.

| Section function | Package offset | Bytes |
|---|---|---:|
| csky_split_rfft_q15 |47914|146|
| csky_split_rifft_q15 |479A8|86|
| csky_shift_q15 |47A00|116|
| csky_abs_max_q15 |47A74|76|
| csky_copy_q15 |47AC0|44|
| csky_fill_q15 |47AEC|40|
| csky_radix4_butterfly_q15 |47D3C|530|
| csky_radix4_butterfly_inverse_q15 |47F50|530|
| csky_bitreversal_16 |48164|38|

All selected bytes lie in the stated BINH B stage2 component span[244032,326092). That span is82060bytes, so selected byte correspondence is1606/82060≈1.9571% of that **stored stage span**. It is not a function, instruction, semantic, source-completeness or whole-firmware coverage percentage: executable denominator, other sections, staging/runtimeplacement and callers have not been established. No denominator can turn nine isolated bodies into complete FFT reconstruction. External twiddle/bit-reversal tables and wrappers/callers remain separately required.

## Provenance accepted with limits

Seven local source-file hashes reproduce. Three DSParchive sampled objects independently hash-match recorded objects; existing target readelf identity matches, exits0 and reproduces every retained DWARF metadata line, including Csourcepaths/types and recorded GNU C11 6.3.0/ck804ef/hardfloat/O2configuration. Fresh resolved debug output and sampled reference objects are retained only in this audit directory.

DWARF proves the archived object's recorded compilation metadata/sourcepath. It does not prove today's local source bytes were the precise compiler input: no independently authenticated original source checksum or rebuild equality is supplied. Same-path edits, assembly counterparts and headers/macros remain possible. All nine object's text equality does not transfer three sampled CU producers to every codec function or uniquely select the stock compiler/SDKcheckout. The nine direct binary correspondences are stronger than names/stringlineage; **source reproducibility remains untested**. Archives are reference inputs, never retained executable substitutes for the byte-identical source target.

A concrete evidence-key caveat: archive member names can repeat (different members share basename), and some original names retain trailing slash. Independent checker resolves by membername plus sectionhash; DWARF samples resolve by objecthash. Owner's sectionhash/archivehash ledger is adequate for these selected hits, but future extraction must preserve objecthash/memberordinal and must not assume basename alone uniquely identifies an archive object. No match-count correction needed.

The three eligible libvma section negative remains narrow; this audit does not reclassify absent hits as vendoralgorithm absence or validate every eligible-section search statistic. Counts381C/185assembly and302debug objects remain owner inventory counts rather than independently reviewed source coverage. Licensing needs per-file notices; root MIT does not replace CMSIS/ARM Apache2/T-HEAD terms.

## Next finite test and result

Accept the nine exact relocation-free section correspondences and1606-byte deduplicated total. No correction to reported total/match result. Tighten any “source-backed” shorthand to distinguish available plausible source plus debug lineage from reproduced source output. Next worthwhile finite step is caller/runtimeplacement and twiddle-table binding for one forward/inverse Q15pair; then recover and independently review its complete pseudocode. A compiler rebuild belongs to the later authorized sourceimplementation gate and is not performed here. No global provider/source exhaustion or producingversion identity follows.
