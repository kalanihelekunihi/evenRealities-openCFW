/* SPDX-License-Identifier: MIT
 * Stock touch application BSS cells at 0x200008c4..0x200009dc.
 * Placement is checked by g2-touch-stockram.ld.inc.
 */
#ifndef G2_TOUCH_RAM_STATE_H
#define G2_TOUCH_RAM_STATE_H

#include <stdint.h>
#include "../config-bootstrap/bootstrap.h"

extern volatile uint8_t touch_eeprom_ready_ram;
extern uint8_t touch_eeprom_context_ram[32];
extern volatile uint32_t touch_gesture_ticks_ram;
extern uint8_t touch_i2c_context_ram[84];
extern uint8_t touch_gesture_state_ram[80];
extern uint8_t touch_report_ram[16];
extern uint8_t touch_i2c_rx_ram[16];
extern uint8_t touch_i2c_tx_ram[16];
extern volatile uint32_t touch_active_budget_ram;
extern volatile uint8_t touch_app_state_ram;
extern volatile uint8_t touch_persist_ram;
extern volatile uint8_t touch_restart_ram;
extern volatile uint8_t touch_save_pending_ram;
extern touch_saved_record touch_saved_record_ram;
extern uint8_t touch_proximity_prior_ram[4];
extern uint8_t touch_widget_processing_ram[24]; /* 0x200009e4..0x200009fc */
extern uint32_t touch_eeprom_provider_ram[12];
extern uint16_t touch_application_threshold; /* reset-copied at 0x200004e8 */

#endif
