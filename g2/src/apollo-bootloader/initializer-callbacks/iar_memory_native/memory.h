#ifndef OPENCFW_IAR_MEMORY_NATIVE_H
#define OPENCFW_IAR_MEMORY_NATIVE_H
#include <stdint.h>
/* RAM-only observed internal helper ABI. Count is bytes, value uses low8.
 * Aligned copy requires nonoverlapping word-aligned pointers in this corpus.
 * Its observed raw return is out+(count&~1), not standard memcpy's out. */
void *opencfw_iar_fill_native(void *out,uint32_t count,uint32_t value);
void *opencfw_iar_aligned_copy_native(void *out,const void *in,uint32_t count);
#endif
