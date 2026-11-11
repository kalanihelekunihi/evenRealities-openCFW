/* Stock 0x4f9ac: EAT touch service initialization command. */
#include <stdint.h>

extern int32_t r1_native_sscanf(const char *input, const char *format, ...);
extern uint32_t r1_conn_field6_get(void);
extern void r1_glasses_connection_role_assign(uint32_t handle);
extern uint32_t r1_service_touch_open(uint32_t source);
extern uint32_t r1_service_touch_close(uint32_t source);
extern void r1_eat_respond_format(const char *format, ...);

void r1_eat_callback_0004f9ac(char *argument)
{
    uint8_t mode = 0u;
    if (r1_native_sscanf(argument, "%hhu", &mode) != 1 || mode > 2u) {
        r1_eat_respond_format(
            "ERROR: Invalid parameter format. Use: AT^TOUCH_INIT=0|1\r\n");
        return;
    }
    if (mode == 1u) {
        r1_glasses_connection_role_assign(r1_conn_field6_get());
        (void)r1_service_touch_open(3u);
    } else if (mode == 0u) {
        (void)r1_service_touch_close(3u);
    }
    r1_eat_respond_format("touch_init enable:%d\r\n", (uint32_t)mode);
}
