/* Native SVC_FlashDBBlobWrite 0x5411f2. Database rows need final placement. */
#include <stdint.h>
extern uint8_t g2_flashdb_db_rows[]; /* native RAM base 0x2005dffc */
extern uint32_t g2_flashdb_candidate_tick(void); /* native 0x4490cc */
extern int32_t audio_flashdb_blob_store(void *,const char *,const void *); /* 0x54503a */

struct audio_flashdb_blob_request {
    const void *data;
    uint32_t length;
};

int32_t audio_flashdb_blob_write(uint32_t index,const char *key,const void *data,uint16_t length) {
    (void)g2_flashdb_candidate_tick();
    struct audio_flashdb_blob_request request={data,(uint32_t)length};
    void *db=g2_flashdb_db_rows+((index&255u)*0x8acu);
    int32_t result=audio_flashdb_blob_store(db,key,&request);
    (void)g2_flashdb_candidate_tick();
    return -result;
}
