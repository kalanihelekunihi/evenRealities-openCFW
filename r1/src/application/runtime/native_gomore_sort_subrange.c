#include <stdint.h>
typedef int32_t (*r1_comparator)(const void *,const void *);
extern void r1_native_qsort(uint8_t *,uint32_t,uint32_t,r1_comparator);
extern int32_t r1_gomore_float_compare_native(const void *,const void *);

/* 0x87600: inclusive bounds use wrapping word arithmetic, then tail qsort. */
void r1_gomore_sort_float_subrange_native(uint32_t values,uint32_t first,uint32_t last)
{
    r1_native_qsort((uint8_t *)(uintptr_t)(values+first*4u),
                   last-first+1u,4,r1_gomore_float_compare_native);
}
