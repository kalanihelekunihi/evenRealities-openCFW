# YHM2710 status native-frame repair

`board/native_yhm_status.c` now uses a ten-byte frame bridge around its C
status logic. Native `0x3529a` saves incoming R3 at caller SP-8, passes that
word to the one-byte register-six read, and restores the complete word into
R3. The previous C provider moved R3 into a compiler local at SP-12. A
controlled replay reproduces that pointer difference even though the old
provider returns the same R0/R3 for an ordinary one-byte transfer.

The new C body receives the native saved word directly. A false readiness
result returns 12. Otherwise the register-read status remains ignored and
the buffer's high nibble supplies the result, with nibble 14 mapped to 17.
An untouched read retains the incoming saved value; no default is added.
The bridge also preserves high-byte changes when a callback writes a full
word. REA and raw instructions agree on the native mapping and frame.

The integration probe passed 32,768 stock/C comparisons. Actual readiness
and register-read frontends execute; GPIO input/probe and the lower
register transport are modeled. Cases span all 256 returned byte values,
four readiness return words, absent/one-byte/two-byte/full-word writes and
eight callback mutation modes. Readiness callbacks change the live pin,
probe function and saved word. Transport statuses vary independently and
callbacks clobber caller-saved registers.

Checks compare GPIO/transport arguments and callback order, R0, full R3,
scratch/configuration bytes, callee-saved registers, SP and interrupt masks.
The transport pointer is exactly caller SP-8 and callbacks remain aligned
to eight bytes. The native readiness callbacks run at SP-16 and transport
at SP-8; C uses SP-24 and SP-16 while retaining the native scratch address.

All 562 R1 units compile without failures or duplicate strong symbols;
the other 561 source units are unchanged. Manifest eligibility and import
sets remain unchanged at 211 application / 34 bootloader, and
`make sources-check` passes. Exact bindings and the old-pointer replay are
in [the machine-readable review](yhm-c-status-frame-review.json).

The C body is 36 bytes plus its ten-byte bridge, versus 112 native bytes.
Private frames, pointer faults, exception behavior, timing, actual GPIO
and PMIC operation, final firmware linking, qualification and whole-image
byte identity remain unproven. The configured probe view does not prove
the final boot configuration. No G2 gate or source-plan selection changes.
