/* Native FlashDB blob-store gateway 0x54503a. */
#include <stdint.h>

extern uint32_t g2_flashdb_db_path(uint32_t); /* native 0x585c94 */
extern int32_t g2_flashdb_print(const char *,...); /* native 0x4733ee */
extern uint32_t audio_flashdb_kv_write(void *,const char *,const void *,uint32_t); /* native 0x544f6c */

static const char prefix[]="[FlashDB][kv]";
static const char names[]="[%s][%s] ";
static const char not_initialized[]="Error: KV (%s) isn't initialize OK.\n";

static uint32_t word(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

uint32_t audio_flashdb_blob_store(void *database,const char *key,const void *request) {
    uint8_t *db=(uint8_t *)database;
    if(db[24u]==0u) {
        (void)g2_flashdb_print(prefix);
        uint32_t path=g2_flashdb_db_path((uint32_t)(uintptr_t)db);
        (void)g2_flashdb_print(names,(const char *)(uintptr_t)word(db),
                               (const char *)(uintptr_t)path);
        (void)g2_flashdb_print(not_initialized,(const char *)(uintptr_t)word(db));
        return 8u;
    }
    uint32_t lock=word(db+28u);
    if(lock!=0u) ((void (*)(void *))(uintptr_t)lock)(db);
    const uint8_t *descriptor=(const uint8_t *)request;
    uint32_t result=audio_flashdb_kv_write(db,key,
                                            (const void *)(uintptr_t)word(descriptor),
                                            word(descriptor+4u));
    uint32_t unlock=word(db+32u);
    if(unlock!=0u) ((void (*)(void *))(uintptr_t)unlock)(db);
    return (uint8_t)result;
}
