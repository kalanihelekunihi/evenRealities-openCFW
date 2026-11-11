/* Source-owned stock EAT command metadata at 0xc419c..0xc43ec. */
#include <stddef.h>
#include "native_eat_command_table.h"
_Static_assert(sizeof(struct r1_eat_command_entry) == 16u,
               "stock EAT command entry size");

extern void r1_eat_callback_0004f160(char *);
extern void r1_eat_callback_0004f0a0(char *);
extern void r1_eat_callback_0004f04c(char *);
extern uint32_t r1_retained_log_printf_sink(const char *,...);
/* Stock 0x4f598 is the AT^RESET_RING assertion site: it prints the assertion
 * banner and source location, then executes a stack-resident fault word. */
void r1_eat_callback_0004f598(char *request)
{
    (void)request;
    (void)r1_retained_log_printf_sink("ASSERTION FAILED!");
    (void)r1_retained_log_printf_sink("File: %s", "..\\..\\..\\platform\\services\\eAT\\at_system.c");
    (void)r1_retained_log_printf_sink("Line: %d", 103);
    (void)r1_retained_log_printf_sink("Function: %s", "at_reset");
    (void)r1_retained_log_printf_sink("Expression: %s", "0");
    __builtin_trap();
}
extern void r1_eat_callback_0004f824(char *);
extern void r1_eat_callback_0004f10c(char *);
extern void r1_eat_callback_0004f040(char *);
extern void r1_eat_callback_0004f524(char *);
extern void r1_eat_callback_0004f77c(char *);
extern void r1_eat_callback_0004ee18(char *);
extern void r1_eat_callback_0004f4d4(char *);
extern void r1_eat_callback_0004f4a4(char *);
extern void r1_eat_callback_0004f9ac(char *);
extern void r1_eat_callback_0004f1f8(char *);
extern void r1_eat_callback_0004f3a0(char *);
extern void r1_eat_callback_0004fa60(char *);
extern void r1_eat_callback_0004f1c4(char *);
extern void r1_eat_callback_0004f650(char *);
extern void r1_eat_callback_0004ee64(char *);
extern void r1_eat_callback_0004ee72(char *);
extern void r1_eat_callback_0004ef18(char *);
extern void r1_eat_callback_0004ef0a(char *);
extern void r1_eat_callback_0004eefc(char *);
extern void r1_eat_callback_0004ee82(char *);
extern void r1_eat_callback_0004eeb8(char *);
extern void r1_eat_callback_0004ee8c(char *);
extern void r1_eat_callback_0004ed34(char *);
extern void r1_eat_callback_0004ed14(char *);
extern void r1_eat_callback_0004f2dc(char *);
extern void r1_eat_callback_0004f2bc(char *);
extern void r1_eat_callback_0004f8e0(char *);
extern void r1_eat_callback_0004f8bc(char *);
extern void r1_eat_callback_0004f94c(char *);
extern void r1_eat_callback_0004f928(char *);
extern void r1_eat_callback_0004f348(char *);
extern void r1_eat_callback_0004f328(char *);
extern void r1_eat_callback_0004eddc(char *);

const struct r1_eat_command_entry r1_eat_command_table[37] = {
    {1u, "AT^INFO", r1_eat_callback_0004f160, 0u},
    {1u, "AT^CHARGE_VER", r1_eat_callback_0004f0a0, 0u},
    {1u, "AT^CHARGE_HW_VER", r1_eat_callback_0004f04c, 0u},
    {1u, "AT^RESET_RING", r1_eat_callback_0004f598, 0u},
    {1u, "AT^DOCK_ADV_SET", r1_eat_callback_0004f824, 0u},
    {0u, "AT^DEVID", r1_eat_callback_0004f10c, 0u},
    {0u, "AT^DFU", r1_eat_callback_0004f040, 0u},
    {0u, "AT^PMIC_READ", r1_eat_callback_0004f524, 0u},
    {0u, "AT^CHARGE_TEMP", r1_eat_callback_0004f77c, 0u},
    {0u, "AT^BAT_ADC", r1_eat_callback_0004ee18, 0u},
    {0u, "AT^PMIC_OFF", r1_eat_callback_0004f4d4, 0u},
    {0u, "AT^PMIC_ISNS", r1_eat_callback_0004f4a4, 0u},
    {0u, "AT^TOUCH_INIT", r1_eat_callback_0004f9ac, 0u},
    {0u, "AT^TOUCH_HW", r1_eat_callback_0004f1f8, 0u},
    {0u, "AT^KV_READ", r1_eat_callback_0004f3a0, 0u},
    {0u, "AT^WEAR_STATUS", r1_eat_callback_0004fa60, 0u},
    {0u, "AT^TEMP", r1_eat_callback_0004f1c4, 0u},
    {1u, "AT^LOG", r1_eat_callback_0004f650, 0u},
    {0u, "AT^BFAST", r1_eat_callback_0004ee64, 0u},
    {0u, "AT^BSLOW", r1_eat_callback_0004ee72, 0u},
    {0u, "AT^STOPADV", r1_eat_callback_0004ef18, 0u},
    {0u, "AT^SLOWADV", r1_eat_callback_0004ef0a, 0u},
    {0u, "AT^FASTADV", r1_eat_callback_0004eefc, 0u},
    {0u, "AT^SDVER", r1_eat_callback_0004ee82, 0u},
    {1u, "AT^BLE_LOG", r1_eat_callback_0004eeb8, 0u},
    {1u, "AT^BLE_KEEPCONNECT", r1_eat_callback_0004ee8c, 0u},
    {2u, "AT^ACC_OPEN", r1_eat_callback_0004ed34, 0u},
    {2u, "AT^ACC_CLOSE", r1_eat_callback_0004ed14, 0u},
    {2u, "AT^HR_OPEN", r1_eat_callback_0004f2dc, 0u},
    {2u, "AT^HR_CLOSE", r1_eat_callback_0004f2bc, 0u},
    {2u, "AT^SPO2_OPEN", r1_eat_callback_0004f8e0, 0u},
    {2u, "AT^SPO2_CLOSE", r1_eat_callback_0004f8bc, 0u},
    {2u, "AT^TEMP_OPEN", r1_eat_callback_0004f94c, 0u},
    {2u, "AT^TEMP_CLOSE", r1_eat_callback_0004f928, 0u},
    {2u, "AT^HRV_OPEN", r1_eat_callback_0004f348, 0u},
    {2u, "AT^HRV_CLOSE", r1_eat_callback_0004f328, 0u},
    {2u, "AT^ACTIVITY_READ", r1_eat_callback_0004eddc, 0u},
};

_Static_assert(sizeof(r1_eat_command_table) == 37u * 16u,
               "stock EAT command table size");
