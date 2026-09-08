# Platform configuration dispatcher

The ten-way dispatcher at image-A package offset 0x17d88 is reconstructed in
`runtime_gx8002_platform_config.c`. Operation zero uses a counted loop for eight
ordered halfword loads and word register writes. The compiler builds its switch
table from C at the original 0x100249a4 address. The original table supplies
comparison evidence only. Compiled code is 196 bytes in a 212-byte envelope;
the generated table occupies the original 40-byte region.

Operations 1–4 and 8 copy a caller word to distinct platform registers.
Operation 5 sets two start-mode registers from a byte and word record.
Operation 7 packs two bytes, copies a halfword, and normalizes two boolean
bytes. Operation 9 reads its input word twice: it writes the first low bit to
0xa000003c, then the second low bit to 0x20027314. Operation 6 and selectors
at least 10 return -1 without accessing the record. Successful operations
return zero. Caller records need the alignment used by each operation.

The decoded comparison executes original and source-generated jump tables,
validates every ordered input read (including its width) and register write,
and checks preserved registers. It covers 77056 scenarios, including all
65536 independent operation-7 packed-byte pairs and distinct operation-9
second-read values. Four rejection/oracle tests protect the checker.

The flash initializer now calls the named source functions recovered so far.
Its full comparison models operation 9 as an input-consuming operation and
includes both writes. The older isolated setup comparison's output-mutation
model is superseded by this recovered contract; it must not be used for
initializer admission. The updated full comparison passes 198 cases, but
still models several services and has a four-byte larger source stack frame.
Flash discovery, callbacks, flash state/interface ownership, and physical
hardware operation are not established by these checks.
