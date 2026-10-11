# CASE framed response send, bounded source candidate

The fixed CASE firmware is `g2-2.2.6.10/firmware_box.bin`, SHA-256
`36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374`.
Original `case_send` occupies `0x0800680c..0x080068b2`; literal words and
the diagnostic format follow. The retained disassembly establishes a fixed
`5a a5 ff` prefix, low-byte length, payload bytes, and low-byte additive
checksum initialized with `length-2`. Each byte goes to the same UART handle
with length one and timeout `0xffff`. Logging checks two RAM bytes before
calling the format logger and hex dump.

`send_provider.c` source-defines this complete bounded parent body for a
readable payload of length at most 65535. UART byte write, formatted logging,
and hex dump remain **explicit lower imports**. The source uses the decoded
diagnostic string `"\n(**%02x**:"`; it does not copy opaque stock bytes.
The original 16-bit loop index can fail to terminate above 65535, so that
range is excluded from the valid source contract.

`verify.py` executes the stock and compiled C in Unicorn, intercepting only
those three lower calls and comparing their complete argument contracts:
UART handle, byte, length and timeout; logger format text and checksum; hex
dump payload and length. It also compares payload memory and PRIMASK. Both
isolated `-Og` and actual CASE archive `-Os` objects pass **28 cases**:
lengths 0, 1, 2, 5, 16, 255, 256 crossed with the four diagnostic flag
states. Receipts are `results.json` and `archive_results.json`. This proves
the bounded parent behavior at its child boundaries. It does not prove
UART driver state, logging output, physical transmission, or delivery.

The deterministic CASE archive rebuild and whole-archive relocatable link
pass with **29 objects, 52 provided symbols, 10 unresolved imports**.
Archive SHA-256:
`30234876bdc8aa5dd6f034a1ce8d112f40f3d612e298be6d55c90e16e2169283`.
The original 12-name direct provider census advances to **5 bounded bodies
complete, 7 direct bodies open**. `case_send` is replaced in the import set
by three named lower providers, so the unresolved symbol count rises from
8 to 10. Seven direct bodies plus these three lower contracts remain; this
is a symbol count, not ten equally sized implementations or a time estimate.
Full CASE startup/link, integrated state and hardware remain open.
