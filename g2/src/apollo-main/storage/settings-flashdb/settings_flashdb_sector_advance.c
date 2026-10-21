/* Native FlashDB GC/sector advance router 0x544c78. */
#include <stdint.h>
extern uint32_t audio_flashdb_gc_count_callback(void *,void *,void *); /* 0x544b84 */
extern uint32_t audio_flashdb_gc_copy_callback(void *,void *,void *); /* 0x544b98 */
extern void *audio_flashdb_scan_iterate(void *,void *,uint32_t,void *,void *,
                                        uint32_t (*)(void *,void *,void *),uint32_t); /* 0x544736 */
void audio_flashdb_sector_advance(void *database,uint32_t requested_size) {
    uint8_t *db=(uint8_t *)database;
    uint8_t sector[24];
    uint32_t count=0u,address=0u;
    (void)audio_flashdb_scan_iterate(db,sector,1u,&count,&address,
                                     audio_flashdb_gc_count_callback,0u);
    if(count<2u) {
        uint32_t context[3]={(uint32_t)(uintptr_t)db,requested_size,address};
        (void)audio_flashdb_scan_iterate(db,sector,0u,context,0,
                                         audio_flashdb_gc_copy_callback,0u);
    }
    db[0x30u]=0u;
}
