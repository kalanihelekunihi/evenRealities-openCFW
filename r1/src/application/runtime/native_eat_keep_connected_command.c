/* Stock 0x4ee8c: keep the BLE connection and acknowledge the command. */
#include <stdint.h>

extern void r1_ble_keep_connected_set(uint32_t enabled);
extern void r1_eat_respond_format(const char *format, ...);

void r1_eat_callback_0004ee8c(char *argument)
{
    (void)argument;
    r1_ble_keep_connected_set(1u);
    r1_eat_respond_format("AT^BLE_KEEPCONNECT+OK\r\n");
}
