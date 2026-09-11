# Gsensor workstate accessor candidate

Package 0xfe94..0xfeac / runtime 0x10206908 reads the word at 0x20026c70,
prints it with the diagnostic at 0x1020adaa, then reads the word again and
returns the second value. The C keeps both volatile reads and uses signed
32-bit formatting for the %d conversion. The diagnostic string supplies the
working name; the state producer, lifecycle and sensor hardware are not yet
established.

Native macOS C-SKY compilation emits 24 bytes, fitting the stock envelope.
The candidate is unregistered and unqualified. Next work must compare decoded
reads, printf forwarding/clobbers and post-call state changes, reconstruct the
diagnostic as source data, and inspect the state references/lifecycle.

Gsensor accessor decoded comparison passes 216 cases and three tests on
macOS. First-read value is printed; second-read value is returned even when
changed during the modeled printf call. Wrong second-read address is rejected.
Printf composition, diagnostic data and state lifecycle remain pending.
Integration 85121 was confirmed live; full source-only goal stays active.

Gsensor diagnostic is source-authored and exact-extent checked at 0x14336.
It passes 144 decoded formatter/output combinations through scripted UART
transmission; six accessor/data tests pass on macOS. Accessor printf boundary
and state lifecycle remain pending. Initializer integration 85121 was confirmed
live; complete source-only firmware remains the active goal.

Gsensor accessor/printf composition passes 144 decoded cases, forwarding
the first state value while returning the second independently of printf.
Seven accessor/data tests pass. Separate frames, translated format pointer
and scripted UART/state values remain explicit limits; state producer/lifecycle
and admission remain pending. Integration 85121 confirmed live; goal active.

Authenticated stock literal inventory found one exact state-address literal
(0x20026c70 at 0xfea4), in the accessor. A neighboring pointer 0x20026c74
appears at 0x1182c. Candidate initialized-data offset 0x18c84 contains one,
but section mapping is explicitly unverified in this inventory. Computed or
indirect writers are not excluded; producer/lifecycle remains unresolved.
Integration 85121 confirmed live; full source-only goal remains active.

Gsensor candidate initialized word is now bounded by authenticated image-A
data region 0x184fc..0x18d90, SHA e0a88003909bb45ae966bfedcbf6e21a5bc83137d26bd36c7f81114fa0034384.
Its value is one. Instruction/data memory alias mapping remains unproved here;
this is not a state initialization or no-writer claim. Neighboring literal
0x20026c74 occurs in a different complex routine; producer remains unresolved.
Integration 85121 confirmed live; full source-only goal stays active.

Pinned SDK mapping evidence (2026-09-08): commit 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5 defines stage-1 IRAM at 0x10000000 and DRAM at 0x20000000, with the same NPU-size offset for stage 2 (`arch/soc/grus/include/soc_config.h`). The linker places SRAM text in IRAM and reserves its size in DRAM before placing initialized data (`arch/soc/grus/link.ld`, lines 345–358). The multiboot loader writes SRAM contents through DRAM then jumps through IRAM (`arch/soc/grus/spl/spl.c`, lines 235–236). This independently supports the alias interpretation; applying it to the stock gsensor word still requires the stock section-layout calculation and does not identify writers. Local source SHA-256 values:

- `arch/soc/grus/include/soc_config.h`: `abda275af6aee96ad676c190e2a72363a79595413336371fced4450f8df76809`
- `arch/soc/grus/link.ld`: `1dc73b74c4b5962a848693ab857e90d34115489a8a7e499897533ad786ff77be`
- `arch/soc/grus/spl/spl.c`: `f3690694fff309c0118579baedb860b1d47c6de3cfb227a977242249568bb56b`

### Gsensor initialized-data mapping checked (2026-09-08)

The state inventory now invokes the stock section analyzer and authenticates the three pinned SDK memory-layout sources before translating the DRAM alias. Address 0x20026c70 maps to package offset 0x18c84, containing the initialized word 1. Four tests pass for section endpoints, rejected out-of-bounds/unaligned addresses, altered stock layout, and altered SDK evidence. This supersedes the earlier unverified mapping note. It does not identify runtime writers, establish hardware behavior, or admit additional source bytes. The full source-only goal remains active.

### Gsensor reader source admission prepared (2026-09-08)

The aggregate reader qualification completed successfully, including decoded before/after-state behavior, printf forwarding, formatter/UART composition and authenticated data mapping. Eleven focused tests pass. The builder now registers the 24-byte C reader and source diagnostic; the initialized state word and its producers remain retained/unresolved. Full integration was started as session 62357, logging to build/gx8002-board/gsensor-integration.log. Do not count the new rows as a verified package checkpoint until that build and package verification complete. The prior verified package remains the 791-test checkpoint.

Neighbor trace: routine 0x11624 loads 0x20026c74 into r10 and indexes it by the original r0 argument retained in r7. Reads occur at 0x116e2/0x11742 and writes at 0x116ea/0x116fa. Four 32-bit arguments (0x3fffffff, 0x7fffffff, 0xbfffffff, 0xffffffff) wrap this address to the sensor word. The low byte of the argument is passed to helper 0x1104c; its rejection behavior and caller constraints remain unresolved. Saved authenticated code hash and decoded evidence in gx8002-gsensor-neighbor.json and .disassembly.txt. No producer exclusion is claimed.

### Channel lookup recovered (2026-09-08)

Recovered helper at package 0x1104c as C: channel 0 returns 0x2002e050, channel 1 returns 0x2002e1cc, other values return null. Native macOS C-SKY compilation produces 28 bytes exactly matching stock (SHA-256 6bfc14e2268d8a026582d4f40694583902020dd40126f5d1bbfa60033f48e4e9). Decoded stock/source replay passes 520 cases. All four wrapping indices previously identified narrow to byte 255 and return null; the caller branches on null at 0x11638 before the array accesses. This narrows the producer search but does not exclude other writers. Lookup is not yet registered for admission. Gsensor integration session 62357 remains live as authoritatively polled; registered inputs were left unchanged.

Channel lookup regression checkpoint: four tests pass, covering both valid channels, all rejected byte values, absence of implicit argument truncation in the lookup itself, and a mutated rejection predicate. The 520-case verifier now checks the caller instructions at 0x1162a/2c/2e/32/36/38, pinning byte narrowing, original-index preservation, helper target and null rejection. Full integration session 62357 was authoritatively polled and remains live. No registered build input was modified in this checkpoint.

Channel lookup source admission is prepared in verify_gx8002_channel_lookup_source.py. A fresh exported ELF and regenerated report pass reviewed_replacements against the saved JSON baseline, admitting one 28-byte C occurrence at package 0x1104c. A tuple/list serialization mismatch in caller evidence was caught by the gate and corrected before this successful rerun. Registration is deferred until the live gsensor integration (session 62357) completes; no new package ownership is claimed yet.
