/* Native FlashDB space-search router 0x544814. */
#include <stdint.h>
extern uint32_t audio_flashdb_space_count_callback(void *,void *,void *); /* 0x5447b6 */
extern uint32_t audio_flashdb_space_match_callback(void *,void *,void *); /* 0x5447e0 */
extern void *audio_flashdb_scan_iterate(void *,void *,uint32_t,void *,void *,
                                        uint32_t (*)(void *,void *,void *),uint32_t); /* 0x544736 */

int32_t audio_flashdb_space_search(void *database,void *sector,uint32_t size) {
    uint8_t *db=(uint8_t *)database;
    int32_t address=-1;
    uint32_t live=0u,deleted=0u;
    uint32_t context[3]={(uint32_t)(uintptr_t)db,size,(uint32_t)(uintptr_t)&address};
    audio_flashdb_scan_iterate(db,sector,0u,&live,&deleted,
                               audio_flashdb_space_count_callback,0u);
    if(deleted!=0u)
        audio_flashdb_scan_iterate(db,sector,2u,context,0,
                                   audio_flashdb_space_match_callback,1u);
    if(live!=0u&&address==-1) {
        if(live<2u&&db[0x30u]==0u)
            db[0x30u]=1u;
        else
            audio_flashdb_scan_iterate(db,sector,1u,context,0,
                                       audio_flashdb_space_match_callback,1u);
    }
    return address;
}
