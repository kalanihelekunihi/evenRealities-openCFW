/* Stock 0x4ee64: factory fast connection-parameter command. */
#include <stdint.h>
extern uint32_t r1_conn_field6_get(void);
extern void r1_app_ble_set_fast_mode_delayed(uint32_t);
void r1_eat_callback_0004ee64(char *argument)
{
 (void)argument;
 r1_app_ble_set_fast_mode_delayed(r1_conn_field6_get());
}
