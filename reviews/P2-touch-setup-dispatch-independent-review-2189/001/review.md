# Independent review 2189

**Result:** PASS_SCOPED.

The source and all receipt-bound files match their declared SHA-256 hashes. Recomputed source slices match code [0x6BD4, 0x6D6A) (406 bytes) and literal pool [0x6D6C, 0x6D74) (8 bytes); the pool words are `0xFFFF0FFF` and `0xC000FFFF`. Independent Capstone Thumb/M-class disassembly matches the candidate listing byte for byte and decodes 199 instructions.

An isolated run regenerated all 144 fixtures exactly. The fixture product covers null/zero and start/end guard cases, 5C8E return 0/128, mode 0/2 reuse behavior, and 6AC0 return 0/2. Assertions check helper order and arguments, fast-path register writes, selected success-path fields and register writes, and R8–R10/SP preservation.

The decoded paths support the pseudocode: invalid arguments return 1; 5C8E result 128 returns 64; 6140's result is ignored; fast reuse requires mode 2 or 4, matching saved start/length, length at most 21, and descriptor bits 13 clear/4 set. Otherwise 6AC0's nonzero status is returned directly; its zero path performs the listed writes before calling 664C and retaining zero. The masks, ordered register updates, and distinct descriptor/register reloads agree with the instructions.

**Limits:** The replay controls 5C8E, 6140, 6AC0 and 664C and uses RAM as the register block. The optional callback path is not exercised; mode 4, predicate-failure variants, arbitrary wrapping arguments, helper side effects and physical peripheral behavior remain unverified. This review makes no whole-firmware completeness or canonical-admission claim.
