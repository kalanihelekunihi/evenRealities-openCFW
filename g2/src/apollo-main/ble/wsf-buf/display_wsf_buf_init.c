/* Native Cordio WsfBufInit 0x530364. Pool storage/configuration are caller owned. */
#include <stdint.h>

struct wsf_pool_desc_init {
    uint16_t size;
    uint8_t count;
    uint8_t reserved;
    void *first;
    void *free_head;
};
struct wsf_pool_config { uint16_t size; uint8_t count; uint8_t reserved; };
_Static_assert(sizeof(struct wsf_pool_desc_init)==12u,"WSF descriptor ABI");
_Static_assert(sizeof(struct wsf_pool_config)==4u,"WSF config ABI");

extern struct wsf_pool_desc_init *audio_wsf_pool_list; /* RAM pointer cell 0x20074eec */
extern volatile uint8_t audio_wsf_pool_count; /* RAM 0x20075044 */
extern volatile uint16_t audio_wsf_pool_used_bytes; /* RAM 0x20074f4a */

/* Stock 0x530364 (WsfBufInit; upstream third-party/local-vendor/sources/AmbiqSuite_R3.2.0/third_party/cordio/wsf/sources/port/freertos/wsf_buf.c) */
uint16_t audio_wsf_buffer_init(uint16_t bytes, void *memory, uint8_t count,
                               const struct wsf_pool_config *config) {
    uint8_t *base=(uint8_t *)memory;
    struct wsf_pool_desc_init *pool=(struct wsf_pool_desc_init *)memory;
    uint8_t *next=base+(uint32_t)count*12u;
    uint8_t *limit=base+(bytes&~7u);
    audio_wsf_pool_list=pool;
    audio_wsf_pool_count=count;
    for(;;) {
        if(next>limit) return 0;
        if(count==0u) {
            uint16_t used=(uint16_t)(next-base);
            audio_wsf_pool_used_bytes=used;
            return used;
        }
        uint16_t size=config->size;
        if(size<8u) size=8u;
        else if((size&7u)!=0u) size=(uint16_t)(size+8u-(size&7u));
        pool->size=size;
        pool->count=config->count;
        pool->first=next;
        pool->free_head=next;
        uint16_t block_size=(uint16_t)(size>>3u);
        uint8_t blocks=pool->count;
        while(blocks>=2u) {
            if(next>limit) return 0;
            *(uint32_t *)next=(uint32_t)(uintptr_t)(next+(uint32_t)block_size*8u);
            next+=(uint32_t)block_size*8u;
            blocks--;
        }
        if(next>limit) return 0;
        *(uint32_t *)next=0;
        next+=(uint32_t)block_size*8u;
        pool++;
        config++;
        count--;
    }
}
