# CASE acknowledgement provider

**COMPLETE bounded source candidate:** `case_ack` at original `0x080068d0..0x080068e8`, 24 bytes, is source-defined in `ack_provider.c`. It copies the authenticated eight-byte literal, substitutes the low command byte, and passes five bytes to `case_send`.

`verify.py` compiles Cortex-M0+ C and executes both original and candidate functions in Unicorn for all 256 command bytes and four high-word cases: **260/260 payload, length and restored-stack comparisons pass**. Both sides intercept only the `case_send` child and compare its exact five-byte argument. Original CASE wrapped SHA is `36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374`; raw SHA is `773b6d4cfdaf0a5a74a557e3babe8222a0ae813436b76a7437c1096d2c60d677`. `results.json` records compiler, source, ELF and original identities.

The CASE archive has 14 objects, 31 provided global names and 23 unresolved names after this addition. The send transport remains a provider boundary; physical UART delivery, retries, RAM layout, production linking and full-payload byte equality are unverified. At least the 23 unresolved provider contracts and integration phases remain; total duration unknown.
