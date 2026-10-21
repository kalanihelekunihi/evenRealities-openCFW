/* Native FlashDB sector preparation wrapper 0x544b78. */
#include <stdint.h>
extern int32_t audio_flashdb_prepare_space(void *,void *,uint32_t); /* 0x544af2 */
int32_t audio_flashdb_prepare_sector(void *database,void *sector,uint32_t key_length,uint32_t value_length) {
    return audio_flashdb_prepare_space(database,sector,key_length+value_length+0x18u);
}
