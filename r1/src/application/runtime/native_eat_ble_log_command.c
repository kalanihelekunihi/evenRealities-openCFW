/* Stock 0x4eeb8: select one of the three structured log backends. */
#include <stdint.h>

extern void r1_structured_log_mode_set(uint32_t mode);
extern void r1_eat_respond_format(const char *format, ...);

void r1_eat_callback_0004eeb8(char *argument)
{
    uint32_t mode;
    if (argument[0] == '0') {
        mode = 1u;
    } else if (argument[0] == '1') {
        mode = 2u;
    } else if (argument[0] == '2') {
        mode = 4u;
    } else {
        r1_eat_respond_format("ERROR TYPE");
        return;
    }
    r1_structured_log_mode_set(mode);
    r1_eat_respond_format("OK");
}
