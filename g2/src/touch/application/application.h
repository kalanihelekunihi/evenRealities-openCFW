/* SPDX-License-Identifier: MIT
 * Touch (PSoC 4000T) product application glue, official 2.2.6.10
 * firmware_touch.bin. Symbols use the g2/symbols/touch.tsv names.
 */
#ifndef G2_TOUCH_APPLICATION_H
#define G2_TOUCH_APPLICATION_H

#include <stdint.h>

/* RAM objects (reset-copied or BSS), stock addresses. */
#define G2_TOUCH_CAPSENSE_CONTEXT ((uint8_t *)0x200004ECu)           /* cy_capsense_context */
#define G2_TOUCH_GESTURE_TICKS    (*(volatile uint32_t *)0x200008E8u) /* SysTick gesture timebase */
#define G2_TOUCH_I2C_CONTEXT      ((void *)0x200008ECu)              /* cy_stc_scb_i2c_context_t, 84 B */
#define G2_TOUCH_GESTURE_STATE    ((uint8_t *)0x20000940u)           /* 80-B gesture machine state */
#define G2_TOUCH_REPORT           ((uint8_t *)0x20000990u)           /* 16-B report scratch */
#define G2_TOUCH_I2C_RX           ((uint8_t *)0x200009A0u)           /* 16-B host write buffer */
#define G2_TOUCH_I2C_TX           ((uint8_t *)0x200009B0u)           /* 16-B host read buffer */
#define G2_TOUCH_ACTIVE_BUDGET    (*(volatile uint32_t *)0x200009C8u)
#define G2_TOUCH_APP_STATE        (*(volatile uint8_t *)0x200009CCu)  /* 1 ACT, 2 ALR, 3 WOT */
#define G2_TOUCH_SAVED_HOLD       (*(volatile uint16_t *)0x200009D6u) /* saved record +6 */
#define G2_TOUCH_DFU_MAILBOX      (*(volatile uint8_t *)0x20000000u)

/* cy_stc_sysint_t layout (PDL 2.21), 8 bytes. */
typedef struct {
    int32_t intrSrc;
    uint32_t intrPriority;
} g2_touch_sysint_config;

void touch_storage_02e4_increment(void);
void touch_platform_0324_configure(void);
void touch_platform_0338_install(uint32_t start);
void touch_platform_0358_sample(void);
void i2c_slave_init(void);
void touch_platform_09a4_start(void);
void timeout_default_1000_if_zero(uint16_t *hold);
__attribute__((noreturn)) void enter_dfu_mailbox_and_reset(uint32_t app);
void touch_product_05e0_bringup(void);
int touch_product_09b4_run(void);

#endif
