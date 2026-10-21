/* Native 0x52ebca: iterate live image rows and send at most 248 bytes per
 * vendor packet. The rows and pointed-to payloads are product runtime data. */
#include <stdint.h>
extern uint32_t audio_ble_radio_image_rows_52e788(uint32_t *,uint32_t *,uint32_t,uint32_t);
extern int32_t audio_ble_radio_write_command_52eaf8(void *,uint32_t,const void *,uint32_t);
extern void audio_ble_radio_progress_52eba8(uint32_t,uint32_t);
extern void audio_ble_hci_boot_log_4733ee(const char *,...);
static const char writing[]="Writing data...\r\n"; /* stock 0x77d920 */
static const char write_error[]="Write data error.\n"; /* stock 0x77d934 */
int32_t audio_ble_radio_update_write_52ebca(void *context,uint32_t total_size) {
    uint32_t count=0u,rows=0u,written=0u;
    int32_t result=0;
    (void)audio_ble_radio_image_rows_52e788(&count,&rows,0u,0u);
    audio_ble_hci_boot_log_4733ee(writing);
    for(uint8_t i=0u;i<count;i++) {
        const uint32_t *row=*(const uint32_t *const *)(uintptr_t)(rows+4u*i);
        uintptr_t data=(uintptr_t)row[0];
        uint32_t remaining=row[1],destination=row[2];
        while(remaining!=0u) {
            uint32_t chunk=remaining>248u?248u:remaining;
            result=audio_ble_radio_write_command_52eaf8(context,destination,
                                                           (const void *)data,chunk);
            if(result!=0) {
                audio_ble_hci_boot_log_4733ee(write_error);
                return result;
            }
            destination+=chunk;data+=chunk;remaining-=chunk;written+=chunk;
            if(total_size!=0u) audio_ble_radio_progress_52eba8(written,total_size);
        }
    }
    return result;
}
