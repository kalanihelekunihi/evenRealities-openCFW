/* Native dmSlaveAdvStopOnDisconnect 0x46dfd0, GattValueUpdate 0x4b5a1e,
 * and appDiscCfgCback 0x533630. The three 16-byte discovery rows are
 * source-owned by the selected subsystem initializer. */
#include <stdint.h>

extern uint8_t *audio_ble_slave_subcontext; /* selected 0x20074334 cell */
extern uint8_t audio_ble_subsystem_rows_200733fc[3u*16u];
extern void audio_ble_service_discovery_restart_531f20(uint8_t);

void audio_ble_gatt_update_child_body(const uint8_t *event)
{
    uint16_t connection=(uint16_t)event[0]|((uint16_t)event[1]<<8);
    uint16_t action=(uint16_t)event[8]|((uint16_t)event[9]<<8);
    if (action!=4u) return;
    uint32_t data_word;
    __builtin_memcpy(&data_word,event+4u,4u);
    const uint8_t *data=(const uint8_t *)(uintptr_t)data_word;
    uint16_t first=(uint16_t)data[0]|((uint16_t)data[1]<<8);
    uint16_t last=(uint16_t)data[2]|((uint16_t)data[3]<<8);
    if (first==0u || first>last) return;
    uint8_t *row=audio_ble_subsystem_rows_200733fc+((uint32_t)connection-1u)*16u;
    uint32_t values_word;
    __builtin_memcpy(&values_word,row+4u,4u);
    if (values_word==0u) return;
    const uint8_t *values=(const uint8_t *)(uintptr_t)values_word;
    uint8_t count=row[10u];
    uint8_t found=0u;
    while (count!=0u) {
        uint16_t value=(uint16_t)values[0]|((uint16_t)values[1]<<8);
        if (first<=value && value<=last) { found=1u; break; }
        values+=2u;
        count=(uint8_t)(count-1u);
    }
    if (found && row[11u]!=1u)
        audio_ble_service_discovery_restart_531f20((uint8_t)connection);
}

/* Stock 0x533630 (appDiscCfgCback, entered as AppDiscServiceChanged). The
 * stock epilogue popped the caller's R3 into R0; the Cordio callers treat it
 * as void, so the entry is an alias of the body. */
__typeof__(audio_ble_gatt_update_child_body) audio_ble_gatt_update_child_533630
    __attribute__((alias("audio_ble_gatt_update_child_body")));

extern uint8_t audio_ble_gatt_value_update_4b5a1e(const uint8_t *subcontext, const uint8_t *event); /* opencfw U5: now provided by the Cordio unit */

void audio_ble_slave_adv_stop_body(const uint8_t *event)
{
    if (event[3u]==0u)
        (void)audio_ble_gatt_value_update_4b5a1e(audio_ble_slave_subcontext,event);
}

/* Stock 0x46DFD0 (dmSlaveAdvStopOnDisconnect). The stock epilogue popped the
 * caller's R7 into R0; the only caller (display_ble_slave_proc_msg.c) declares
 * it void, so the entry is an alias of the body. */
__typeof__(audio_ble_slave_adv_stop_body) dmSlaveAdvStopOnDisconnect
    __attribute__((alias("audio_ble_slave_adv_stop_body")));
