/* Native FlashDB GC copy callback 0x544b98. */
#include <stdint.h>
struct sector_info;
extern uint32_t g2_flashdb_write_status(uint32_t,uint32_t,uint8_t *,uint32_t,uint32_t,uint32_t); /* 0x5858d8 */
extern uint32_t g2_flashdb_read_kv(uint32_t,void *); /* 0x544000 */
extern uint32_t audio_flashdb_gc_move(uint32_t,void *); /* 0x5449c0 */
extern uint32_t g2_flashdb_next_kv_addr(uint32_t,const void *,const void *); /* 0x543f8c */
extern uint32_t audio_flashdb_gc_erase(uint32_t,uint32_t,uint32_t); /* 0x5445f2 */
extern uint32_t g2_flashdb_next_sector_addr(uint32_t,const void *,uint32_t); /* 0x544374 */
extern uint32_t g2_flashdb_read_sector_info(uint32_t,uint32_t,struct sector_info *,_Bool); /* 0x54418e */
extern uint32_t g2_flashdb_db_path(uint32_t); /* 0x585c94 */
extern int32_t g2_flashdb_print(const char *,...); /* 0x4733ee */

static const char prefix[]="[FlashDB][kv]";
static const char names[]="[%s][%s] ";
static const char move_failed[]="Error: Moved the KV (%.*s) for GC failed.\n";
static uint32_t word(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static void put_word(uint8_t *p,uint32_t value) {
    p[0]=(uint8_t)value;p[1]=(uint8_t)(value>>8);
    p[2]=(uint8_t)(value>>16);p[3]=(uint8_t)(value>>24);
}

uint32_t audio_flashdb_gc_copy_callback(void *record,void *context_arg,void *unused) {
    (void)unused;
    uint8_t *sector=(uint8_t *)record;
    uint8_t *context=(uint8_t *)context_arg;
    uint32_t db=word(context);
    if(sector[0u]==0u||(sector[2u]!=2u&&sector[2u]!=3u)) return 0u;

    uint32_t address=word(sector+4u);
    uint8_t status[4];
    (void)g2_flashdb_write_status(db,address+1u,status,4u,3u,1u);
    uint8_t kv[88];
    put_word(kv+80u,address+0x10u);
    for(;;) {
        (void)g2_flashdb_read_kv(db,kv);
        if(kv[1u]!=0u&&(kv[0u]==2u||kv[0u]==3u)&&audio_flashdb_gc_move(db,kv)!=0u) {
            (void)g2_flashdb_print(prefix);
            uint32_t path=g2_flashdb_db_path(db);
            (void)g2_flashdb_print(names,(const char *)(uintptr_t)word((const uint8_t *)(uintptr_t)db),
                                   (const char *)(uintptr_t)path);
            (void)g2_flashdb_print(move_failed,(uint32_t)kv[2u],(const char *)(kv+16u));
        }
        uint32_t next=g2_flashdb_next_kv_addr(db,sector,kv);
        put_word(kv+80u,next);
        if(next==UINT32_MAX) break;
    }
    (void)audio_flashdb_gc_erase(db,address,UINT32_MAX);
    uint32_t old=word(context+8u);
    put_word(context+8u,address);
    put_word((uint8_t *)(uintptr_t)db+20u,g2_flashdb_next_sector_addr(db,sector,0u));
    uint8_t next_sector[24];
    uint32_t read=g2_flashdb_read_sector_info(db,old,(struct sector_info *)(void *)next_sector,1);
    if(read==0u&&word(context+4u)<word(next_sector+16u)) return 1u;
    return 0u;
}
