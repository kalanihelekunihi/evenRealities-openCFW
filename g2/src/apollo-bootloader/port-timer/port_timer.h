#ifndef OPENCFW_BOOTLOADER_PORT_TIMER_H
#define OPENCFW_BOOTLOADER_PORT_TIMER_H

#include <stdint.h>

/* Recovered no-argument startup hook at stock address 0x0041b6fa.
 * Its R0 return is an inherited R3 value and is not a status contract. */
uint32_t opencfw_bl_port_timer_configure(void);

/* Recovered helper interfaces used by the configure hook and differential
 * fixtures. Their units follow the raw ABI; no tick frequency is asserted. */
void opencfw_bl_port_timer_gate_enable(uint32_t bits);
void opencfw_bl_port_timer_irq_priority(int32_t irq, int32_t priority);
void opencfw_bl_port_timer_irq_enable(int32_t irq);
uint32_t opencfw_bl_port_timer_clock_configure(uint32_t value);
uint32_t opencfw_bl_port_timer_read_counter(void);
uint32_t opencfw_bl_port_timer_compare_set(uint32_t compare_id,
                                           uint32_t delta);

/* These clock-manager providers remain an explicit platform dependency.
 * The bootloader calls them through stock clock_request/release adapters. */
uint32_t clock_request(uint32_t clock_id_register, uint32_t user_id_register);
uint32_t clock_release(uint32_t clock_id_register, uint32_t user_id_register);

#endif
