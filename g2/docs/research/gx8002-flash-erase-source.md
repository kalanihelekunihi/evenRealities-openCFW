# Range and chip erase reconstruction

The range routine at package0x15d6c becomes160/168 C bytes with
-fno-move-loop-invariants; its valid-address frame is12 bytes versus stock24.
The chip wrapper at0x15e14 is20-byte exact and delegates address0/usable size.

Qualification passes1152 boundary/clobber cases,32 wrapper cases and three
complete wrapping sequences. Calls, encoder arguments, command selection,
return values and ABI preservation match decoded stock. Helpers are modeled.
The source rounds the starting address down to4KiB, clamps the wrapped end to
usable size, then chooses64KiB erases when aligned and sufficiently long,
otherwise4KiB. A zero-length unaligned request still erases one sector.

Unsigned wrap is preserved explicitly. Request(address0x1000,length0xffffffff,
size0xff000) makes65,551 erase iterations, ending at address0. Request
(0xfffff000,0x2000,0xffffffff) makes two iterations across address zero;
(0x80000001,0x80000000,0xffffffff) makes32,769 iterations ending at zero.
All three full traces and termination match stock. This documents original
behavior, not a hardware recommendation. Eight oracle/rejection tests pass.

Reviewed admission adapter is prepared; integration remains pending. The
address encoder now takes a const volatile uint32_t pointer, matching the
state field; its compiled bytes are unchanged and baseline was regenerated.
Physical erase, device behavior and whole firmware execution remain unqualified.

Both routines are now integrated through reviewed admission. All172 native
macOS codec tests, full package assembly and artifact verification pass.
This replaces188 retained bytes with180 compiled bytes and eight fill bytes.
Address-encoder pointer provenance was revalidated by the full build. Physical
erase behavior remains unqualified; no hardware was accessed.
