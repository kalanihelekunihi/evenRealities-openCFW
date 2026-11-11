/* Stock 0x4f04c/0x4f0a0: consume the dock hardware and version reports. */
#include <stdint.h>

extern uint32_t r1_st25dvxxkc_dock_hardware_get(void);
extern void r1_st25dvxxkc_dock_hardware_clear(void);
extern const char *r1_st25dvxxkc_dock_version_get(uint8_t *length);
extern void r1_st25dvxxkc_dock_version_clear(void);
extern void r1_eat_respond_format(const char *format, ...);

void r1_eat_callback_0004f04c(char *argument)
{
    (void)argument;
    const uint32_t hardware = r1_st25dvxxkc_dock_hardware_get();
    if (hardware != 0u) {
        r1_eat_respond_format("charging dock hw:%u\r\n", hardware);
        r1_st25dvxxkc_dock_hardware_clear();
    } else {
        r1_eat_respond_format("charging dock hw:NULL\r\n");
    }
}

void r1_eat_callback_0004f0a0(char *argument)
{
    (void)argument;
    uint8_t length = 0u;
    const char *const version = r1_st25dvxxkc_dock_version_get(&length);
    if (version != 0 || length != 0u) {
        r1_eat_respond_format("charging dock version:%s\r\n", version);
        r1_st25dvxxkc_dock_version_clear();
    } else {
        r1_eat_respond_format("charging dock version:NULL\r\n");
    }
}
