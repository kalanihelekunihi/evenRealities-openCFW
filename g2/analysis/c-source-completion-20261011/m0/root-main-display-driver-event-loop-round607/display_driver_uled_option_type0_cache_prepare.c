/* Apollo S200 cache preparation at 0x47510e. */
#include <stdint.h>

static inline void barrier(void) {
    __asm__ volatile("dsb sy\n\tisb sy" ::: "memory");
}

uint32_t display_driver_uled_prepare_transfer_47510e(const uint32_t *range) {
    uint32_t cache=*(volatile const uint32_t *)(uintptr_t)0xe000ed14u;
    if ((cache&0x00010000u)==0u) {
        barrier();
        return 0u;
    }
    if (range==0) {
        *(volatile uint32_t *)(uintptr_t)0xe000ed84u=0u;
        __asm__ volatile("dsb sy" ::: "memory");
        uint32_t geometry=*(volatile const uint32_t *)(uintptr_t)0xe000ed80u;
        uint32_t ways=(geometry>>13)&0x7fffu;
        uint32_t sets=(geometry>>3)&0x3ffu;
        for (uint32_t w=ways;;w--) {
            for (uint32_t s=sets;;s--) {
                *(volatile uint32_t *)(uintptr_t)0xe000ef6cu=
                    ((w&0x1ffu)<<5)|(s<<30);
                if (s==0u) break;
            }
            if (w==0u) break;
        }
        barrier();
        return 0u;
    }
    uint32_t address=range[0];
    uint32_t length=range[1];
    if ((int32_t)length<=0) return 0u;
    int32_t remaining=(int32_t)((address&31u)+length);
    __asm__ volatile("dsb sy" ::: "memory");
    do {
        *(volatile uint32_t *)(uintptr_t)0xe000ef68u=address;
        address+=32u;
        remaining=(int32_t)((uint32_t)remaining-32u);
    } while (remaining>0);
    barrier();
    return 0u;
}
