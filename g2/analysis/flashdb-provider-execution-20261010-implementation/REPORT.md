# FlashDB bounded provider execution and name-limit discrimination

## Result

The sealed predecessor's status wording is corrected by **CORRECTION.md**: stock tests the low byte, not the entire return register. Status R0=0x100 proceeds to the mocked flash-write; 0x101 suppresses it and returns 1. Original firmware functions and genuine pinned-source function bodies agree across 23 bounded O0 comparisons, with explicitly modeled provider boundaries. Thirty-two original name guards and 160 source guard projections select name limit 64 among 61–65.

Source pin is official FlashDB `714d6159e7e6afb267a3953756abca445c350e61`. No canonical source admission, physical flash write, production implementation or byte-equality claim follows.

## Provider comparisons

`candidate.c` contains unchanged extracted bodies of get_kv, fdb_kv_get_blob and write_kv_hdr, with pinned public/low-level headers, recovered candidate configuration and explicit provider declarations. Source-owned wrapper functions expose the private bodies. Diagnostic logging is replaced with a stopping boundary; uninitialized source logging/return is not compared to stock. Apple clang compiles ARM32 Thumb Cortex-M4, O0, short enums; objects link with GNU ARM ld. Stub bodies contain BKPT and must be intercepted by the emulator. These are test seam stubs, not production implementations.

`results.json` retains every original/source trace and output:

* Ten get_kv cases cover found/missing, requested length below/equal/above recorded length, zero request/value, null buffer, null value-length output, and ignored read error. A null-buffer maximum-word length case proves arithmetic projection only. Real stock get_kv runs; find_kv and flash-read are mocks. The find mock writes the full 88-byte synthetic KV record with value_len+12 and value-address+84. Flash-read records arguments and returns an injected result without accessing backing flash or modifying the output buffer.
* Four initialized get-blob cases execute real stock get_kv transitively, including optional lock/unlock combinations and missing key. Mock locks record database identity/order. Return lengths, full blob/output bytes, traces and stack restoration agree. The uninitialized stock case separately stops at the first real logging-call boundary; no logging implementation or final return is fabricated.
* Nine write-header cases cover status0/1/6, flash results0/2/6, raw status0x100/0x101 and raw flash result0x100/0x101. Status arguments are database/address/header/6/1/false. On zero low byte, flash-write arguments are database/address+4/header+4/20/false. Guest code only writes stack/output metadata; header and value buffer remain unchanged. Neither mock programs flash.

Five write cases use byte-sized enum provider values. Four inject full raw register words into original stock. For the corresponding source comparison, its short-enum providers return the byte-normalized value; this is an explicit boundary projection, not proof that a valid C provider returns 0x100. Additional raw injections into the O0 source comparator are retained separately and happen to match the sampled stock outcomes.

`raw-O1-results.json` preserves the optimizer boundary: O1 source write_kv_hdr assumes the short-enum return ABI and omits stock's defensive UXTB. Raw 0x100/0x101 injections therefore differ from stock, whereas byte-normalized source providers match. These synthetic values are outside the valid declared enum provider contract. No known stock caller/provider is shown to deliver them. Likewise direct get_kv inputs are broader than the previously examined application adapter, which narrows length to 16 bits; high-word/null argument fixtures do not establish live caller reachability or buffer admissibility.

The initial O1 get_kv comparison failed one address projection and remains unexplained (first-attempt-limits.txt). O1 read/provider equivalence is not claimed. The accepted 23-case comparator is separately compiled O0. These finite checks establish neither compiler instruction equality nor all-input behavior.

## Name-limit constraint

Stock create_kv_blob begins at 0x544D60. It calls original strlen at 0x44A43C, compares its result with **65** at 0x544D7E, and accepts unsigned lengths below 65 at 0x544DAA. Rejection reaches the first logging boundary 0x4733EE; the static rejection path also loads diagnostic argument64 and eventual FDB_KV_NAME_ERR5. Fixtures stop at accepted-prefix or first diagnostic boundary, before allocation/header construction/storage logic.

Lengths0,60,61,62,63,64,65,66 at each of four pointer alignments execute the original strlen and guard: lengths through64 accept,65/66 reject. Source projections retain the exact pinned `if (strlen(key) > FDB_KV_NAME_MAX)` branch and independently compiled simple source strlen, varying limit61–65. Only64 matches all32 stock decisions. This discriminates the nearby name-limit equivalence class left by aligned struct offsets; it does not prove source revision uniqueness or full create behavior. The source projection's accepted return0 is a test completion marker, not create_kv_blob's return.

## Receipts, preservation and limits

`original-receipts.json` binds all five exercised original ranges to locked raw SHA-256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`. Named byte excerpts, exact source/compiler inputs, emitted ELF files, compiler commands, scripts and all outputs are retained. Linux Unicorn execution uses the existing isolated container, not physical hardware. Source/provider methods remain mocks even when their addresses correspond to genuine stock functions.

Cache-member/loop constraints are owned by discovery and were not investigated here. Whole find_kv, status/read/write/FAL implementation, physical flash delivery, compiler producer, complete source corpus and byte-identical rebuild remain unresolved. Independent review of this continuation is pending. Preservation receipts verify existing seals, 110 audit inputs and four checkpoints; the index is stable during verification. Earlier seals, production, submodule pins and index were not edited.
