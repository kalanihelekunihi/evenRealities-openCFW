/* Independent host IEEE binary64 -> binary32 cast oracle. */
#include <stdint.h>
#include <string.h>
uint32_t convert_bits(uint64_t bits) { double d; float f; uint32_t out; memcpy(&d,&bits,8); f=(float)d; memcpy(&out,&f,4); return out; }
