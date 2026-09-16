/* SPDX-License-Identifier: MIT */
/* Stock-compatible RT calloc; multiplication intentionally wraps at 32 bits. */
#include <stdint.h>
#include <stddef.h>
extern void *rt_malloc(uint32_t);
extern void *memset(void *, int, size_t);
void *backup_rt_calloc(uint32_t count, uint32_t size)
{
    uint32_t bytes=count*size;
    void *result=rt_malloc(bytes);
    if (result) memset(result,0,bytes);
    return result;
}
