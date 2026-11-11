/* Stock 0x4f160: firmware, board, BLE name and controller address report. */
#include <stdint.h>
#include "ble_gap.h"

extern const char r1_device_info_firmware[];
extern const char r1_device_info_hardware[];
extern const char *r1_identity_data_ptr_get(void);
extern void r1_adc_error(uint32_t status);
extern void r1_eat_respond_format(const char *format,...);

void r1_eat_callback_0004f160(char *argument)
{
    (void)argument;
    ble_gap_addr_t address={0};
    uint32_t status=sd_ble_gap_addr_get(&address);
    if(status)r1_adc_error(status);
    r1_eat_respond_format(
        "[soft %s][hard %s][ble name %s]"
        "[ble addr %02X:%02X:%02X:%02X:%02X:%02X]",
        r1_device_info_firmware,r1_device_info_hardware,
        r1_identity_data_ptr_get(),
        (uint32_t)address.addr[5],(uint32_t)address.addr[4],
        (uint32_t)address.addr[3],(uint32_t)address.addr[2],
        (uint32_t)address.addr[1],(uint32_t)address.addr[0]);
}
