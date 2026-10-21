/* Native SVC_KvdbBlobWrite 0x4d957e. */
#include <stdint.h>
extern int32_t audio_flashdb_blob_write(uint32_t,const char *,const void *,uint16_t); /* 0x5411f2 */
int32_t audio_settings_kvdb_blob_write(const char *key,const void *data,uint32_t length) {
    return audio_flashdb_blob_write(0u,key,data,(uint16_t)length);
}
