/* IAR DLIB (EWARM 9.x) abs, firmware 2.2.6.10, native 0x509694..0x50969b
 * (CMP R0,#0; IT MI; NEGMI R0,R0; BX LR). IAR DLIB has no public source;
 * this is the freestanding equivalent written from the disassembly. */
#include <stdint.h>

int32_t iar_abs_509694(int32_t x);

int32_t iar_abs_509694(int32_t x)
{
    if (x < 0)
        x = -x;
    return x;
}
