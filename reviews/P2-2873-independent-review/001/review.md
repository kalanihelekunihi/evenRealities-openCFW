# Independent review 2873

Status: **PASS_SCOPED** (`accepted: false`).

The pinned bootloader source and decoded ITCM image match their inventory hashes. The provider body `[0x4213D8, 0x421548)` matches its claimed digest, and the candidate receipt and listed artifact hashes verify. I ran the candidate replay with a fresh output path; all 8,640 fixtures passed.

The fixtures execute the original provider decision body, original address helpers, original copy wrapper, and the original ITCM word-copy loop without function interception. The test matrix is 9 selector values, 10 offsets, 3 positive counts, 4 configuration values, 2 enable states, 2 destination values, and 2 PRIMASK values. It checks provider/copy arguments, status, copy-loop iteration count, destination contents, boundary sentinels, preserved registers, stack pointer, and PRIMASK. Synthetic source words follow the declared address-XOR pattern. The destination assertions are consistent with the copy loop's word loads/stores and decrementing count.

The evidence is limited to those synthetic mapped buffers and positive counts. It does not prove physical source behavior, zero-count/overflow copies, overlap/fault behavior, or caller/startup reachability. No canonical admission is claimed.
