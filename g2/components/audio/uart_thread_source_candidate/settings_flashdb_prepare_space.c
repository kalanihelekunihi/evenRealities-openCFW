/* Native FlashDB allocation and one-GC retry 0x544af2. */
#include <stdint.h>
extern int32_t audio_flashdb_space_search(void *,void *,uint32_t); /* 0x544814 */
extern void audio_flashdb_sector_advance(void *,uint32_t); /* 0x544c78 */
extern uint32_t g2_flashdb_db_path(uint32_t); /* 0x585c94 */
extern int32_t g2_flashdb_print(const char *,...); /* 0x4733ee */
static const char prefix[]="[FlashDB][kv]";
static const char names[]="[%s][%s] ";
static const char full[]="Error: Alloc an KV (size %hu) failed after GC. KV full.\n";
static uint32_t word(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
int32_t audio_flashdb_prepare_space(void *database,void *sector,uint32_t size) {
    uint8_t *db=(uint8_t *)database;
    uint8_t retried=0u;
    int32_t result;
    for(;;) {
        result=audio_flashdb_space_search(db,sector,size);
        if(result!=-1) return result;
        if(db[0x30u]==0u||retried!=0u) break;
        audio_flashdb_sector_advance(db,size);
        retried=1u;
    }
    if(retried!=0u) {
        (void)g2_flashdb_print(prefix);
        uint32_t path=g2_flashdb_db_path((uint32_t)(uintptr_t)db);
        (void)g2_flashdb_print(names,(const char *)(uintptr_t)word(db),
                               (const char *)(uintptr_t)path);
        (void)g2_flashdb_print(full,size);
        db[0x30u]=0u;
    }
    return result;
}
