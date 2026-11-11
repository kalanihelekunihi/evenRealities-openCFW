/* SPDX-License-Identifier: MIT
 * Stock 0x0800a19a/0x0800a24a/0x0800a310 config-channel (PA3, "2510") bit
 * waveforms. Call-for-call with stock: pulse leaves 0x0800a1ca/0x0800a206
 * (bus-pulse/pulse_leaves.c), GPIO leaves 0x0800baa4/bad8/bafc and the
 * 5-cycle-per-count delay 0x0800a7a2 (the earlier volatile stack counter
 * ran 2.2x slow).
 */
#include <stdint.h>
extern void case_pulse8_short(void);                  /* 0x0800a1ca */
extern void case_pulse8_long(void);                   /* 0x0800a206 */
extern void case_bus_drive_a(void);                   /* 0x0800bad8 */
extern void case_bus_drive_b(void);                   /* 0x0800baa4 */
extern void case_bus_drive_c(void);                   /* 0x0800bafc */
extern void case_boot_short_delay_a7a2(uint32_t count); /* 0x0800a7a2 */
/* Stock 0x0800A19A (case_route_boolean_alt) */
void case_bus_start(uint32_t bit)
{
    if(bit!=0u)case_pulse8_long();
    else case_pulse8_short();
}
/* Stock 0x0800A24A (case_pulse8_extended) */
void case_bus_finish(void)
{
    case_bus_drive_a();case_bus_drive_b();case_bus_drive_a();
    case_boot_short_delay_a7a2(0x17u);case_bus_drive_c();case_boot_short_delay_a7a2(0x15eu);
    case_bus_drive_a();
}
/* Stock 0x0800A310 (case_pulse8_double_train) */
void case_bus_prepare(void)
{
    case_bus_drive_a();case_bus_drive_b();case_bus_drive_a();case_bus_drive_c();
    for(int32_t i=0;i<10;++i)case_boot_short_delay_a7a2(0x15eu);
    case_bus_drive_a();case_boot_short_delay_a7a2(0x17u);case_bus_drive_c();
    for(int32_t i=0;i<10;++i)case_boot_short_delay_a7a2(0x15eu);
    case_bus_drive_a();
}
