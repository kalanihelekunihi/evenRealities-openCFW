/* Pinned LittleFS lookahead allocation, stock 0x4cb186. */
#include <stdint.h>
extern int32_t g2_lfs_alloc_scan(void *filesystem);
extern void g2_lfs_no_space_log(uint32_t block);
static uint32_t *word_at(void *base,uint32_t offset) {
    return (uint32_t *)((uint8_t *)base+offset);
}
int32_t g2_lfs_alloc(void *filesystem,uint32_t *block) {
    uint32_t *next=word_at(filesystem,0x5cu),*size=word_at(filesystem,0x58u);
    uint32_t *checkpoint=word_at(filesystem,0x60u);
    uint32_t count=*word_at(filesystem,0x6cu);
    const uint8_t *lookahead=(const uint8_t *)(uintptr_t)*word_at(filesystem,0x64u);
    for(;;) {
        while(*next<*size) {
            if((lookahead[*next/8u]&(1u<<(*next%8u)))==0u) {
                *block=(*word_at(filesystem,0x54u)+*next)%count;
                do {
                    ++*next;--*checkpoint;
                } while(*next<*size &&
                        (lookahead[*next/8u]&(1u<<(*next%8u)))!=0u);
                return 0;
            }
            ++*next;--*checkpoint;
        }
        if(*checkpoint==0u) {
            g2_lfs_no_space_log((*word_at(filesystem,0x54u)+*next)%count);
            return -28;
        }
        int32_t err=g2_lfs_alloc_scan(filesystem);
        if(err) return err;
    }
}
