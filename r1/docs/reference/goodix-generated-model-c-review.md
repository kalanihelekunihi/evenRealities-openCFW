# R1 generated SpO2 model construction in C

The [native graph review](goodix-model-graph-c-review.md) supersedes the graph assembly boundary. Graph construction and seven helpers now execute as C; eleven executor identity data bindings remain unresolved.

Five native entries now have one C implementation in `r1/src/application/goodix/native_spo2_generated_model.c`: the generated constructor (`0x99014`), dense descriptor (`0x74be0`), recurrent descriptor (`0x74a20`), and two executor identity accessors (`0x74cdc`, `0x74bd8`). The [machine-readable receipt](goodix-generated-model-c-review.json) pins inputs, objects, fixtures and results.

The constructor allocates 836 bytes, builds two graph records and constructs the dense/recurrent descriptors. The recurrent state allocation is 64 bytes for this model. Descriptors preserve raw float bits, byte-sized flags, wrapping cursor arithmetic, allocator callback timing and the native clear-before-null-check order. No graph failure guard or cleanup was invented.

All 5,794 stock/C comparisons pass, including independent complete-instance, descriptor, cursor and zero-state oracles. All 128 complete C constructor/heap/teardown lifecycles release the model and state allocations to the original heap top. Twenty compiled defects are rejected. Of 478 native instruction bytes, 476 execute; the two-byte branch at `0x9910a` is unreachable after the explicit return. Source execution cannot enter stock code. Model resource pointers are normalized only in comparison results.

The tested object matches the normal build. All 884 units compile and compose without duplicate strong symbols; 873 prior nongenerated source/object pairs remain unchanged. There is no new writable state. Application imports increase from 63 to 67 because the constructor import is replaced by graph assembly and four opaque executor address data bindings. Boot imports remain 22. Those bindings supply identity words; no executor calling ABI or inference implementation is assumed.

Graph construction, executor implementation, numerical inference, cold floating-point activation, concurrency, invalid pointers, physical sensors, final executable linking/startup and boot remain open. Extreme dimension cases establish logical word arithmetic rather than physically valid large allocations. The successful build is an `ld -r` composition, not a bootable firmware image. Byte identity is waived for the current work.
