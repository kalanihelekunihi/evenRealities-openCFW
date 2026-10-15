/* Native FlashDB sector scanner 0x544736, distinct from KV iterator 0x5443b0. */
#include <stdint.h>
struct sector_info;
extern uint32_t g2_flashdb_read_sector_info(uint32_t,uint32_t,struct sector_info *,_Bool); /* 0x54418e */
extern uint32_t g2_flashdb_next_sector_addr(uint32_t,const void *,uint32_t); /* 0x544374 */

static uint32_t word(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

void *audio_flashdb_scan_iterate(void *database,void *sector,uint32_t mode,
                                 void *arg1,void *arg2,
                                 uint32_t (*callback)(void *,void *,void *),uint32_t refresh) {
    uint8_t *db=(uint8_t *)database;
    uint8_t *record=(uint8_t *)sector;
    uint32_t traversed=0u;
    uint32_t current=word(db+20u);
    for(;;) {
        traversed+=word(db+12u);
        (void)g2_flashdb_read_sector_info((uint32_t)(uintptr_t)db,current,
                                          (struct sector_info *)(void *)record,0);
        if((uint8_t)mode==0u||(uint8_t)mode==record[1u]) {
            if((uint8_t)refresh!=0u)
                (void)g2_flashdb_read_sector_info((uint32_t)(uintptr_t)db,current,
                                                  (struct sector_info *)(void *)record,1);
            if(callback!=0&&callback(record,arg1,arg2)!=0u)
                return arg1;
        }
        current=g2_flashdb_next_sector_addr((uint32_t)(uintptr_t)db,record,traversed);
        if(current==UINT32_MAX) return arg1;
    }
}
