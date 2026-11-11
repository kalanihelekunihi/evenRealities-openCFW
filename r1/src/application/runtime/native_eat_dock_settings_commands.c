/* Stock 0x4f77c/0x4f824: parsed dock temperature and advertisement settings. */
#include <stdint.h>

extern int32_t r1_native_sscanf(const char *input, const char *format, ...);
extern void r1_st25dvxxkc_dock_temperature_limit_set(uint32_t value);
extern void r1_st25dvxxkc_dock_advertisement_set(uint32_t value);
extern void r1_eat_respond_format(const char *format, ...);

void r1_eat_callback_0004f77c(char *argument)
{
    uint32_t parsed = 0u;
    const int32_t fields = r1_native_sscanf(argument, "%d", &parsed);
    const uint32_t temperature = (uint8_t)parsed;
    r1_st25dvxxkc_dock_temperature_limit_set(temperature);
    if (fields == 1 && temperature <= 60u) {
        r1_eat_respond_format("set charge temperature save value:%d\r\n",
                              temperature);
    } else {
        r1_eat_respond_format(
            "ERROR: Invalid parameter format. Use: AT^CHARGE_TEMP=20~60\r\n");
    }
}

void r1_eat_callback_0004f824(char *argument)
{
    uint32_t parsed = 0u;
    const int32_t fields = r1_native_sscanf(argument, "%d", &parsed);
    if (fields == 1 && parsed <= 1u) {
        r1_st25dvxxkc_dock_advertisement_set((uint8_t)parsed);
        r1_eat_respond_format("charging dock adv open flag:%d\r\n", parsed);
    } else {
        r1_eat_respond_format(
            "ERROR: Invalid parameter format. Use: AT^DOCK_ADV_SET=0|1\r\n");
    }
}
