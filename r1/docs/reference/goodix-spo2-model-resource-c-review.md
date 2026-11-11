# R1 SpO2 model resource and forwarding head in C

The [generated model review](goodix-generated-model-c-review.md) supersedes the constructor and descriptor boundary: five entries now use C. Graph assembly and four opaque executor address data bindings remain unresolved.

`r1/src/application/goodix/native_spo2_model_resource.c` supplies the readonly model parameters, native weights accessor and checked forwarding head. The [machine-readable receipt](goodix-spo2-model-resource-c-review.json) pins REA evidence, C sources, objects, model-data hash, tests and normal build.

All 883 units compile and compose without duplicate strong symbols. Two imports are replaced by one generated-constructor import, reducing application imports from 64 to 63; bootloader imports remain 22. No writable state is added.

| Native entry | C provider |
| --- | --- |
| `0x6a018` | `r1_goodix_spo2_weights_get` |
| `0x36c26` | `r1_goodix_spo2_model_create` — forwarding head only |

The accessor returns a stable, aligned C object containing 3,924 numeric words: 15,696 model-data bytes corresponding to stock `0xad1ac..0xb0efb`. Every compiled byte matches the pinned reference. Its ELF section is readonly and nonexecuting, and its symbol is an object. This is parameter/coefficient data, not an executable firmware region or opcode array.

The forwarding head reads only parameter word one. Null weights return null without calling the generated constructor. Nonnull weights are passed unchanged, and the full returned pointer is forwarded, including when the provider changes the parameter record. The generated constructor at `0x99014` remains unimplemented.

Stock execution independently establishes the resource extent. Its seven cursor endpoints are 1,756, 3,512, 7,384, 7,492, 14,828, 15,644 and 15,696 bytes. Construction allocates 836 and 64 bytes. Running from the stock data, a RAM rebase, and the compiled C resource produces identical constructed records after adjusting resource pointers. The data remains unchanged and is never executed in these runs. Construction reads only 48 header bytes directly and carries references to the remaining coefficients; inference-time coefficient use and numerical output remain unverified.

All 546 direct stock/C comparisons pass, covering all 16 native accessor/head instruction bytes, null/non-null and extreme pointer words, field offsets, parameter mutation, buffer seeds and interrupt masks. Independent oracles check the single field read, call count, forwarded pointer and return. All resource bytes are compared.

A further 582 constructor comparisons execute the actual C session/queue graph, weights accessor and forwarding head. The 128 real-C-heap/complete-teardown cases model only generated construction, which returns null and excludes its allocations. Every allocation made by recovered C code coalesces back to the prior top. Modeled calls return through BX LR, and source tests cannot execute stock. The separate native construction runs are analysis evidence, not retained firmware execution bodies.

Ten compiled defects are rejected: wrong parameter field, omitted null check, discarded or truncated result, wrong accessor offset, corruption of the first or last resource word, mutable resource placement, low-bit-only gating, and truncated weights pointers. The mutable-resource case is rejected by the independent ELF placement check.

Final probes use the exact normal-build compiler arguments, and the tested object equals the normal object. All 872 prior nongenerated source/object pairs remain unchanged. Existing generated startup and uecc objects differ; source-plan and cache layout remain unchanged.

Saved registers, SP, masks and guards are checked. Invalid parameter addresses, caller scratch, APSR, private frames, cold FP activation, concurrency and physical hardware remain outside the proof. Generated model construction/inference, other algorithm and hardware dependencies, final executable linking/startup and device boot remain open. Relocatable composition is not bootable firmware; data equality does not establish instruction or image identity.
