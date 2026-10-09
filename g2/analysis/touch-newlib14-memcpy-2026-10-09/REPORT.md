# Flash memcpy dependency: genuine source-provider closure

Unmodified newlib source at the official Arm14.2 metadata revision
`7923059bff6c120c6fb74b63c7553ea345c0a8f3` regenerates the complete18byte
stock memcpy extent `[0xAA2C,0xAA3E)`. There are no executable relocations.
The installed libc_nano.a provider matches; regular libc.a's172byte section
differs. This is a source/provider discriminator, not unique stock-toolchain
identification or a claim that every firmware call uses nano libc.

The authenticated ARM memcpy-stub.c source includes the generic string body
when size optimization is selected. That source is preserved, not replaced
with a handwritten wrapper. A focused -Os Cortex-M0+/Thumb compilation with
real installed nano.specs/header configuration matches stock bytes. Official
Category2 recipes independently support nano.specs; these flags are not
asserted to reproduce the vendor's complete libc build command.

Seven exact-revision source/license files were acquired from the newlib source
mirror; URLs, byte counts and hashes are in acquisition.json. The mirror pin
comes from official release metadata, not from matching bytes. Source notices
and COPYING.NEWLIB are retained. The original Sourceware Gitweb endpoint was
not accessible through the browsing tool; mirror acquisition does not imply a
signature or original distribution-server authentication claim. All actually
consumed source/vendor headers and generated configuration are hashed in
results.json. Recreating that full generated header/build configuration is
outside this focused provider experiment.

128original-instruction cases pass for lengths0/1/2/3/4/15/16/128 and all
source/destination byte alignments0–3. The routine copies forward one byte per
iteration, preserves guards, r4 and SP, and returns the original destination.
Tests use non-overlapping synthetic RAM and prove no overlap contract or device
timing. This supplies the real byte-copy dependency for the flash stack-buffer
path; it does not execute SROM or flash writes. Cases are in original-results.json.

Readable interface: `void *memcpy(void *dst, const void *src, size_t n)` returns
dst after copying n bytes. Input validity is caller-owned; overlapping buffers
remain outside the source contract. Zero length copies no byte. No opcode
arrays, retained executable blobs or replacement stubs were used as source.

Independent review is pending. No54entrycensus increment, campaign admission,
whole-source completeness or physical flash/power claim. Proposed optional
comparison reference, not installed: `third-party/reference/newlib-arm14`,
upstream `https://sourceware.org/git/newlib-cygwin.git`, revision above.
No Git, production, device or shared campaign-state changes.
