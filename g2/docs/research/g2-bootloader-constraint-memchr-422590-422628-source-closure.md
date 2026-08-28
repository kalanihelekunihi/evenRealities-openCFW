# G2 bootloader constraint-dispatch and `memchr` source closure

The two authenticated executable bodies surrounding the retained message pool
at `[0x00422590,0x00422628)` now compile from maintained MIT C at
their exact stock addresses. The 28-byte constraint dispatcher has SHA-256
`0fb60f3cb36d88d77e7767e201951f1c239fe41b874b911a24b87b6e93b31e6c`;
its sole direct call is relocated to the retained default constraint handler at
`0x00417C28`. The 88-byte `memchr` has SHA-256
`ed4dd5b44329c11e723cdca6aa56a749fb62673c7839ca6da4dac59483a4be9b`
and is byte-identical to the Apollo-main IAR DLIB `memchr` at `0x004D40E0`.
The intervening 36-byte pool/message span has SHA-256
`6a1c3b3c218a63a0485994c42f851a99bff4fedd5443396ba4a7bbe7a1ba5b25`
and remains authenticated official data; it contains the handler cell address
`0x20027190` and `constraint handler: bad message`.

`runtime_constraint_memchr_422590.c` is 3,149 bytes with SHA-256
`8522f0356e55269e26bd841ccd455fb7444a85a4c0aa62a028f46425e4356323`.
The constraint body has unrelocated SHA-256
`be06721c80e8c9de0e7333e48a077bf90fb79ce00131ba8573f9fc0eb46787f9`;
the relocation-free `memchr` hash is the installed hash above. Null constraint
messages select the retained message, a registered handler receives
`(message, NULL, 0x22)`, the default path calls the retained handler, and both
paths return `0x22`. The memory search truncates the needle to one byte,
supports unaligned prefixes and aligned word scanning, returns the first match,
and handles zero length and misses.

Five focused tests pin both bodies, the pool, the two direct callers and the
shared Apollo-main body; exercise registered/default/null constraint behavior
and aligned/unaligned search boundaries; and compile both reviewed Cortex-M55
profiles. Canonical accounting becomes 19,675 source-owned, 16,528 generated
patch, 16 alignment, and 127,621 retained official bytes, including 362 cave
bytes and 4,088 exact in-place bytes across 241 source-owned functions and 201
patch sites. Provider and unsigned-package hashes remain unchanged. The
4,603,816-byte flash plan has SHA-256
`208dc810d0959a9b957172d82f40a3ddaa4120652f05f915885862a31be73b56`
with 6,615 placed, two unresolved, five container-only and six protected
regions.

No hardware operation occurred. The handler registration cell, retained
default handler, callers, memory accessibility and fault behavior require
authorized Apollo510 evidence. That evidence is unavailable because no
authorized responsive right temple exists and the left temple must remain
stock. Firmware-wide functional completeness is not claimed; the next
executable body begins at `0x00422628`.
