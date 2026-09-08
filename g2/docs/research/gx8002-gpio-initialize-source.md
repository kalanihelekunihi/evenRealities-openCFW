# GPIO initialization source recovery

Stock0xf65c/runtime0x102060d0,24bytes. The authenticated SDK gpio_mini.o
relocation identifies the call as gx_clock_set_module_enable. Recovered C
calls the existing source-owned platform gate with module4,enable1, writes0
to0xa0001034, then returns0. Its declaration matches the platform gate's
void(unsigned int,unsigned int) definition.

Native macOS compilation exactly matches all24stock bytes, SHA
a94629e7633a0e3d039e4a24a3f9856f9246d423152e2e250caaa885f584c05c.
The structural verifier requires the full nine-instruction sequence and
4-byte saved-return frame, including rebuilding the MMIO pointer after the
helper call. Four tests pass for ordered effects and wrong helper/register/
frame rejection. Gate body semantics remain separately qualified; no
hardware electrical behavior is proven. Candidate is not yet registered.

Integrated alongside SPI-list initialization. All637 tests and full macOS
package build/verification pass; byte-identical C leaves payload hashes
unchanged.
