/* SPDX-License-Identifier: MIT
 * Isolated 0xa3 three-producer status report with source-owned formats.
 */
#include <stdint.h>
extern uint32_t case_legacy_value_a(uint32_t *out);
extern uint32_t case_legacy_value_b(uint32_t *out);
extern uint32_t case_legacy_value_c(uint32_t *out);
extern uint32_t case_legacy_logger(const char *format, ...);
static const char case_a3_prefixed[] = "****** B200 vol:%d pct:%d, open:%d, usb:%d, cur:%d, GLS_L:%d, GLS_R:%d temp:%d";
static const char case_a3_plain[] = "{\"vol\":%d,\"pct\":%d,\"open\":%d,\"usb\":%d,\"cur\":%d,\"GLS_L\":%d,\"GLS_R\":%d,\"temp\":%d}";
static const char case_a3_newline[] = "\r\n";
static uint32_t report(const char *format, uint32_t a,uint32_t b,uint32_t c)
{
    const volatile uint8_t *const fields=(const volatile uint8_t *)(uintptr_t)0x2000087cu;
    return case_legacy_logger(format,c,fields[1],fields[4],fields[3],b,fields[16],fields[17],a);
}
uint32_t case_legacy_a3_branch(const uint8_t *command, uint32_t length)
{
    (void)command;(void)length;
    uint32_t a=0,b=0,c=0;
    (void)case_legacy_value_a(&a);
    (void)case_legacy_value_b(&b);
    (void)case_legacy_value_c(&c);
    const volatile uint8_t *const flag=(volatile uint8_t *)(uintptr_t)0x200000bfu;
    if (*flag==0u) {
        (void)report(case_a3_prefixed,a,b,c);
        (void)case_legacy_logger(case_a3_newline);
        if (*flag==0u)return 0u;
    }
    (void)report(case_a3_plain,a,b,c);
    return case_legacy_logger(case_a3_newline);
}
