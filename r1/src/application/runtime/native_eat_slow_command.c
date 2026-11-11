/* Stock 0x4ee72: request the immediate slow connection mode. */
#include <stdint.h>

extern uint32_t r1_conn_field6_get(void);
extern void r1_app_ble_set_slow_mode(uint32_t, uint32_t);

void r1_eat_callback_0004ee72(char *argument)
{
    (void)argument;
    r1_app_ble_set_slow_mode(r1_conn_field6_get(), 1u);
}
