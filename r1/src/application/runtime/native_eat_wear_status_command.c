/* Stock 0x4fa60: report the current wear/health mode as a Boolean. */
#include <stdint.h>

extern uint32_t r1_health_mode_get(void);
extern void r1_eat_respond_format(const char *format, ...);

void r1_eat_callback_0004fa60(char *argument)
{
    (void)argument;
    r1_eat_respond_format("wear_status:%d\r\n",
                          r1_health_mode_get() != 0u ? 1u : 0u);
}
