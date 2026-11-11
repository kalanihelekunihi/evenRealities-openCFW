#ifndef R1_NATIVE_PEAK_SELECTION_H
#define R1_NATIVE_PEAK_SELECTION_H
#include <stdint.h>
/* Native668dc: signed16 input; count0 still reads input0; u16 output index. */
void r1_goodix_native_minimum_row(const void *,uint32_t,void *);
/* Native66900: descriptor u16[length,rows]; accumulate existing u16 output. */
void r1_goodix_native_peak_mask(const void *,const void *,void *);
/* Native36734: fixed37-row descriptor; float input and u16 selected indices. */
void r1_goodix_native_peak_indices(const void *,int32_t,int32_t,int32_t,void *,void *);
#endif
