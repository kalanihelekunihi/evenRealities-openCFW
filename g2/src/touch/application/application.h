/* SPDX-License-Identifier: MIT
 * Touch (PSoC 4000T) product application glue, official 2.2.6.10
 * firmware_touch.bin. Symbols use the g2/symbols/touch.tsv names.
 */
#ifndef G2_TOUCH_APPLICATION_H
#define G2_TOUCH_APPLICATION_H

#include <stdint.h>
#include "ram_state.h"
#include "../reset-layout/reset_capsense_context.h"

/* RAM objects (reset-copied or BSS), stock addresses. */
#define G2_TOUCH_CAPSENSE_CONTEXT ((uint8_t *)&touch_reset_capsense_context)
#define G2_TOUCH_GESTURE_TICKS    touch_gesture_ticks_ram
#define G2_TOUCH_I2C_CONTEXT      ((void *)touch_i2c_context_ram)
#define G2_TOUCH_GESTURE_STATE    touch_gesture_state_ram
#define G2_TOUCH_REPORT           touch_report_ram
#define G2_TOUCH_I2C_RX           touch_i2c_rx_ram
#define G2_TOUCH_I2C_TX           touch_i2c_tx_ram
#define G2_TOUCH_ACTIVE_BUDGET    touch_active_budget_ram
#define G2_TOUCH_APP_STATE        touch_app_state_ram /* 1 ACT, 2 ALR, 3 WOT */
#define G2_TOUCH_SAVED_HOLD       touch_saved_record_ram.parameter
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
