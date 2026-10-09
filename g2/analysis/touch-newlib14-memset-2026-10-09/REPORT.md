# Genuine memset source-provider match

Unmodified generic newlib memset.c at vendor-pinned revision
7923059bff6c120c6fb74b63c7553ea345c0a8f3 regenerates all16stock bytes at
`[0xA9D4,0xA9E4)`. The nano archive provider also matches, without executable
relocations. The focused -Os/Thumb/Cortex-M0+ contract and real vendor nano
headers are the same independently supported contract used for memcpy.
Source/license/header/input/command/object/archive hashes are in results.json.
No original or production implementation was edited, no wrapper/stub supplied.

The byte-fill loop stores the low8bits of the value, copies exactly n bytes
and returns the original destination.224original-instruction fixtures cover
four alignments, zero/small/128byte lengths and seven values including high
bits and allones. Guard bytes and byte-write addresses are verified. These are
synthetic caller-valid RAM observations, not physical or concurrent memory
claims. Source/object equality is selected provider evidence, not unique
producer, vendor full configuration reproduction or whole-image completeness.

This adds16newreview-pending source-comparator bytes outside the54entrycensus.
License evidence is the pinned COPYING.NEWLIB retained by the reviewed memcpy
packet; no blanket license inference is made. Proposed reference is the same
newlib release-pin comparison reference, not another submodule or checkout.
