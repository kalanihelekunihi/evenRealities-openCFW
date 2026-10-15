/* Apollo BLE master cache insertion 0x503568. */
#include <stdint.h>

extern volatile uint8_t audio_ble_subsystem_state_20071670[];
extern uint32_t audio_ble_master_mode_get_536a00(void);
extern uint32_t audio_ble_privacy_compare_address(const uint8_t *,const uint8_t *);
extern void audio_ble_copy_address6_4d293c(void *,const void *);

void audio_ble_master_child_503568(void *message,void *record)
{
    (void)record;
    const uint8_t *source=(const uint8_t *)message;
    for (uint8_t index=0u;index<10u;++index) {
        volatile uint8_t *row=audio_ble_subsystem_state_20071670+
                              (uint32_t)index*0x0fu;
        uint32_t alternate=audio_ble_master_mode_get_536a00();
        if (alternate==0u) {
            if (row[6]==source[6] &&
                audio_ble_privacy_compare_address((const uint8_t *)row,
                                                  source+7u)!=0u)
                return;
            if (row[6]==0xffu) {
                row[6]=source[6];
                row[0x0eu]=source[0x0eu];
                audio_ble_copy_address6_4d293c((void *)row,source+7u);
                row[7]=source[0x14u];
                audio_ble_copy_address6_4d293c((void *)(row+8u),source+0x15u);
                audio_ble_subsystem_state_20071670[0x96u]++;
                return;
            }
        } else {
            if (row[6]==source[0x0bu] &&
                audio_ble_privacy_compare_address((const uint8_t *)row,
                                                  source+0x0cu)!=0u)
                return;
            if (row[6]==0xffu) {
                row[6]=source[0x0bu];
                audio_ble_copy_address6_4d293c((void *)row,source+0x0cu);
                row[7]=source[0x12u];
                audio_ble_copy_address6_4d293c((void *)(row+8u),source+0x13u);
                audio_ble_subsystem_state_20071670[0x96u]++;
                return;
            }
        }
    }
}
