# SpO2 packet layout correction

The [numeric-decoder review](goodix-spo2-decode-c-review.md) adds actual C decoding and nominal TIA gain state. Real frame/core/assembler/decoder replays agree with stock; fixed power calls become verified exact constants. Thirteen later processing stages remain unfinished.

The [channel-assembly review](goodix-spo2-assemble-c-review.md) adds the real C assembler and parity helpers, with live enable/PPG integrity effects checked through the C core. The remaining numeric decoder is explicit as `r1_goodix_spo2_decode`; the complete computation engine is still unfinished.

The native assembler reads12 bytes through the enable-mask pointer. In the stock frame, its four mask bytes are immediately followed by PPG samples. The former C arrays were separate; the tested compiler placed gain bytes after the mask. Earlier checks covered only four mask bytes and missed this dependency.

`native_spo2_execute.c` now uses one52-byte object containing the four mask bytes followed by12 PPG words. Static assertions fix the PPG offset at4. The input enable pointer addresses the complete object byte view, so integrity writes to PPG samples remain visible to later prefix reads.

**4,433 stock-versus-C pairs pass**:1,044 direct and3,389 dispatcher cases. The direct fixture checks prefix bytes and live aliasing after a temporary PPG write. The dispatcher checks adjacency/prefix bytes while running all five actual frame adapters. The original compiled separate-array object fails this layout oracle. Existing packet, floating-point, full RAM, saved-register and selected-fault checks still pass.

All **901 units** compile and compose;890 other nongenerated source/object pairs are unchanged. No persistent state, imports or newly admitted stock functions are added. Imports remain91 application/22 bootloader; source-plan/cache files remain unchanged.

The computation stages remain modeled in these fixtures. This corrects the producer/consumer memory contract; it does not establish a complete SpO2 engine, physical sampling or bootable firmware.

[Machine-readable evidence](goodix-spo2-packet-layout-c-review.json) pins the source, old/new objects, REA evidence and checks.
