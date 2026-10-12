/* Native WsfBufFree 0x5304d4: reverse class-range lookup and locked push. */
#include <stdint.h>
#include <stddef.h>

struct wsf_pool_desc_data;
extern struct wsf_pool_desc_data *audio_wsf_pool_list; /* RAM 0x20074eec */
extern volatile uint8_t audio_wsf_pool_count;          /* RAM 0x20075044 */
extern void WsfCsEnter(void);
extern void WsfCsExit(void);

void WsfBufFree(void *buffer) {
    uintptr_t base=(uintptr_t)audio_wsf_pool_list;
    uintptr_t row=base+(uintptr_t)audio_wsf_pool_count*12u;
    for (;;) {
        row-=12u;
        if (row<base) return;
        uintptr_t first=*(const uint32_t *)(const void *)(row+4u);
        if ((uintptr_t)buffer>=first) break;
    }
    WsfCsEnter();
    uint32_t *block=(uint32_t *)buffer;
    block[1]=0xfaabd00du; /* authenticated ROM literal at 0x530534 */
    block[0]=*(uint32_t *)(void *)(row+8u);
    *(uint32_t *)(void *)(row+8u)=(uint32_t)(uintptr_t)buffer;
    WsfCsExit();
}
