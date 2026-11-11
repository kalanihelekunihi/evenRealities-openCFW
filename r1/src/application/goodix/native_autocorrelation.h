#ifndef R1_NATIVE_AUTOCORRELATION_H
#define R1_NATIVE_AUTOCORRELATION_H
#include <stdint.h>
/* Native0x92a04: positive lengths; padding in 2*max(n,m)-1 words is untouched. */
void r1_goodix_native_full_correlation(const void *,uint32_t,const void *,uint32_t,void *);
/* Native0x928da and0x928ca. Factor uses hard-float S0; count can be zero. */
void r1_goodix_native_vector_scale(float,const void *,void *,uint32_t);
void r1_goodix_native_vector_scale_veneer(float,const void *,void *,uint32_t);
/* Native0x666a4: positive count; uses actual heap and maximum-index provider. */
void r1_goodix_native_normalized_autocorrelation(const void *,uint32_t,void *);
#endif
