/* Native FlashDB KV write core 0x544f6c. */
#include <stdint.h>
extern uint32_t g2_log_candidate_module_length(const uint8_t *); /* 0x44a43c */
extern uint32_t g2_flashdb_find_kv(uint32_t,uint32_t,void *); /* 0x54449a */
extern int32_t audio_flashdb_prepare_sector(void *,void *,uint32_t,uint32_t); /* 0x544b78 */
extern uint32_t audio_flashdb_kv_delete(void *,const char *,void *,uint32_t); /* 0x5448b4 */
extern uint32_t audio_flashdb_store_value(void *,void *,const char *,const void *,uint32_t); /* 0x544d60 */
extern void audio_flashdb_sector_advance(void *,uint32_t); /* 0x544c78 */

uint32_t audio_flashdb_kv_write(void *database,const char *key,const void *data,uint32_t length) {
    uint8_t *db=(uint8_t *)database;
    uint32_t result=0u;
    if(data==0)
        return (uint8_t)audio_flashdb_kv_delete(db,key,0,1u);

    uint32_t key_length=g2_log_candidate_module_length((const uint8_t *)key);
    if(audio_flashdb_prepare_sector(db,db+0x8cu,key_length,length)==-1)
        return 7u;

    uint32_t found=g2_flashdb_find_kv((uint32_t)(uintptr_t)db,
                                      (uint32_t)(uintptr_t)key,db+0x34u);
    if((uint8_t)found!=0u)
        result=audio_flashdb_kv_delete(db,key,db+0x34u,0u);
    if((uint8_t)result==0u)
        result=audio_flashdb_store_value(db,db+0x8cu,key,data,length);
    if((uint8_t)found!=0u&&(uint8_t)result==0u)
        result=audio_flashdb_kv_delete(db,key,db+0x34u,1u);
    if(db[0x30u]!=0u) {
        uint32_t first=g2_log_candidate_module_length((const uint8_t *)key);
        (void)g2_log_candidate_module_length((const uint8_t *)key);
        audio_flashdb_sector_advance(db,length+first+0x18u);
    }
    return (uint8_t)result;
}
