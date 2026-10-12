/* Native 0x52e7c0 and 0x52ec84 walk live image rows, compare controller
 * CRC with local payload CRC, and retain their distinct return semantics. */
#include <stdint.h>
extern uint32_t audio_ble_radio_image_rows_52e788(uint32_t *,uint32_t *,uint32_t,uint32_t);
extern int32_t audio_ble_radio_crc_remote_52e6ac(void *,uint32_t,uint32_t,uint32_t *);
extern uint32_t audio_ble_radio_crc_local_4d34f8(const void *,uint32_t,const uint32_t *);
extern void audio_ble_hci_boot_log_4733ee(const char *,...);
static const char mismatch[]="crc mismatch, actual_crc:0x%x,  expected_crc:0x%x\r\n";
static const char remote_fail[]="send crc32 calc failed, status:%d\r\n";
static const char check_begin[]="\r\nChecking data...\r\n";
static const char check_fail[]="Failed to calculate CRC32\n";
static const char check_mismatch[]=
    "Invalid CRC32 from 0x%08x to 0x%08x (0x%08x instead of 0x%08x)\n";

uint32_t audio_ble_radio_update_current_52e7c0(void *context) {
    uint32_t count=0u,rows=0u;
    (void)audio_ble_radio_image_rows_52e788(&count,&rows,0u,0u);
    for(uint8_t i=0u;i<count;i++) {
        const uint32_t *row=*(const uint32_t *const *)(uintptr_t)(rows+4u*i);
        uint32_t actual=0u,start=row[2],length=row[1];
        int32_t result=audio_ble_radio_crc_remote_52e6ac(context,start,start+length,&actual);
        if(result!=0) {
            audio_ble_hci_boot_log_4733ee(remote_fail,result);
            return 1u;
        }
        uint32_t expected=audio_ble_radio_crc_local_4d34f8((const void *)(uintptr_t)row[0],length,0);
        if(actual!=expected) {
            audio_ble_hci_boot_log_4733ee(mismatch,actual,expected);
            return 0u;
        }
    }
    return 1u;
}

int32_t audio_ble_radio_update_check_52ec84(void *context) {
    uint32_t count=0u,rows=0u;
    (void)audio_ble_radio_image_rows_52e788(&count,&rows,0u,0u);
    audio_ble_hci_boot_log_4733ee(check_begin);
    for(uint8_t i=0u;i<count;i++) {
        const uint32_t *row=*(const uint32_t *const *)(uintptr_t)(rows+4u*i);
        uint32_t actual=0u,start=row[2],length=row[1];
        int32_t result=audio_ble_radio_crc_remote_52e6ac(context,start,start+length,&actual);
        if(result!=0) {
            audio_ble_hci_boot_log_4733ee(check_fail);
            return result;
        }
        uint32_t expected=audio_ble_radio_crc_local_4d34f8((const void *)(uintptr_t)row[0],length,0);
        if(actual!=expected) {
            audio_ble_hci_boot_log_4733ee(check_mismatch,start,start+length,actual,expected);
            return 14;
        }
    }
    return 0;
}
