# Independent review 6113

**Result:** PASS_SCOPED.

The source and dependency/artifact hashes match. All ledger bytes match the locked image, and [0x429e00, 0x429f68) tiles exactly as 129 Thumb instructions over 360 bytes; GNU `arm-none-eabi-objdump` independently confirms the boundaries.

The 40-byte frame saves R2/R3/R4-R10/LR, and the first metadata byte at SP0 overwrites saved R2; SP4 retains initial R3. The second-row high field is retained for adjustment, while row/metadata reads and later register publications follow the packet’s fresh-read order. The polling branch uses fresh status reads and tests bit 30; it delays/increments below 60 only while clear. The R8-R7 delta is doubled only when signed >=1, then the sum is compared unsigned against 128 for low-seven-bit saturation. Later fresh register reads clear bits 16 and 25. The routine calls 0x42a1bc with R4/R5, ignores the result, and POP aliases R0 to SP0 metadata and R1 to initial R3 at SP4 while restoring R4-R10/PC/SP.

**Limits:** Static review only; no execution rerun. This does not establish child behavior, hardware purpose, bounds safety, channel semantics, canonical admission, or C/freeze gates. Private evidence remains `accepted:false`.
