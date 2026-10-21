/* SPDX-License-Identifier: MIT
 * Stock 0x0800a1ca/0x0800a206 are constant-delay forms of
 * 0x0800a19a; also 0x0800a24a/0x0800a310 bus waveform composition.
 * Four pin/timing leaves remain typed platform contracts.
 */
#include <stdint.h>
extern void case_bus_drive_a(void);    /* 0x0800bad8 */
extern void case_bus_drive_b(void);    /* 0x0800baa4 */
extern void case_bus_drive_c(void);    /* 0x0800bafc */
extern void case_bus_delay(uint32_t); /* 0x0800a7a2 */
void case_bus_start(uint32_t bit)
{
    case_bus_drive_a();case_bus_drive_b();case_bus_drive_a();
    case_bus_drive_c();case_bus_delay(bit?0x5au:0x17u);case_bus_drive_a();
}
void case_bus_finish(void)
{
    case_bus_drive_a();case_bus_drive_b();case_bus_drive_a();
    case_bus_delay(0x17u);case_bus_drive_c();case_bus_delay(0x15eu);
    case_bus_drive_a();
}
void case_bus_prepare(void)
{
    case_bus_drive_a();case_bus_drive_b();case_bus_drive_a();case_bus_drive_c();
    for(uint32_t i=0;i<10u;++i)case_bus_delay(0x15eu);
    case_bus_drive_a();case_bus_delay(0x17u);case_bus_drive_c();
    for(uint32_t i=0;i<10u;++i)case_bus_delay(0x15eu);
    case_bus_drive_a();
}
