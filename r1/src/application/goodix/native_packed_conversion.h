#ifndef R1_NATIVE_PACKED_CONVERSION_H
#define R1_NATIVE_PACKED_CONVERSION_H
#include <stdint.h>
/* Native28de0/28de6 return binary32 through hard-float S0. */
float r1_goodix_native_unpack_5_10(uint32_t);
float r1_goodix_native_unpack_6_9(uint32_t);
/* Native28dd4/28dda receive binary32 through S0; packed result is in R0. */
uint32_t r1_goodix_native_pack_5_10(float);
uint32_t r1_goodix_native_pack_6_9(float);
/* Native28dec: signed count; live reads/stores; callback uses S0/R0. */
void r1_goodix_native_pack_array(void *,const void *,int32_t,uint32_t (*)(float));
#endif
