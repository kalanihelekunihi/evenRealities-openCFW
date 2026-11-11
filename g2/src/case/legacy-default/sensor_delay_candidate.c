/* SPDX-License-Identifier: MIT
 * Stock 0x0800a408 and 0x0800a148 loop semantics.
 * 0x0800a408 is the PMIC/fuel-gauge bus bit delay. Stock is
 * "movs; (adds; uxtb; cmp; bcc) x10; bx" = 52 cycles. The counter is an asm
 * operand so the compiler keeps that loop instead of folding it (a volatile
 * stack counter took about twice as long). Checked with
 * build/case-link/timing.py: SCL/SDA intervals match stock within 11 cycles.
 * At SYSCLK 64 MHz one bit is about 284 cycles (stock 288): SCL about 225 kHz,
 * tHIGH 92 cycles (1.44 us), tLOW about 190 cycles (3.0 us), data set-up
 * at least 1.4 us. That is inside I2C fast-mode limits (400 kHz, tHIGH >= 0.6 us,
 * tLOW >= 1.3 us) for the CW2217 gauge (0x64) and the PMIC (0x38). The
 * replaced inline copy ran at about 410 cycles per bit (156 kHz).
 */
#include <stdint.h>

/* Stock 0x0800A408 (case_delay_10) */
uint32_t case_binary_sensor_delay(void)
{
    uint8_t count=0u;
    do { __asm__ volatile("":"+r"(count)); count=(uint8_t)(count+1u); } while(count<10u);
    return count;
}

/* Dedup (0x0800a148): case_binary_sensor_delay_count is an alias of case_policy_timer_delay (startup/application_policy_timer_query_candidate.c). */
extern uint32_t case_binary_sensor_delay_count(uint32_t count);
