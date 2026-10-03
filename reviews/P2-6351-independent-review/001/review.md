# Independent review 6351

Disposition: **PASS_SCOPED**; `accepted:false`.

Packet and locked-source hashes match for 0x42DAE8–0x42DB74. GNU Thumb decoding confirms the 44-byte register save plus 20 local bytes (64-byte frame). The descriptor pointer and output pointer are recovered from their saved incoming stack slots at SP24 and SP20. The descriptor word is masked to 24 bits and reduced by 32 with wrap; a separately reloaded descriptor pointer supplies the base at offset 20. The call to 0x42D9F0(base, length) is ignored.

The routine stages base, length, literal and tag 288 in stack slots and calls 0x4176CE with the listed register arguments. It calls 0x42D84C(1), loads the literal-selected first argument, calls 0x4153A4(first, selected-address), and stores the returned word through a freshly reloaded output pointer. It then reloads that pointer and output word. On zero, it stages the literal and tag 291 and calls 0x4176CE, ignores the result, and branches to 0x42DC8A. On nonzero it calls 0x4154D2(output-word, 32, 0), ignoring the return. The extent ends during that path. The input pointers are dereferenced without null checks in this range.

Continuation, cleanup, and callee purposes remain unresolved. No filesystem, hardware/runtime, C-equivalence, or admission claim is made; no canonical files or gates changed.
