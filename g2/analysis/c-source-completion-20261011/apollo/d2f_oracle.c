/* Host-only bit oracle for the pinned compiler-rt helper. */
#include <stdint.h>
extern float __truncdfsf2(double);
uint32_t source_bits(uint64_t raw)
{
    double in; float out; uint32_t bits;
    __builtin_memcpy(&in,&raw,8);
    out=__truncdfsf2(in);
    __builtin_memcpy(&bits,&out,4);
    return bits;
}
uint32_t hardware_bits(uint64_t raw)
{
    double in; float out; uint32_t bits;
    __builtin_memcpy(&in,&raw,8);
    volatile double hold=in;
    out=(float)hold;
    __builtin_memcpy(&bits,&out,4);
    return bits;
}
