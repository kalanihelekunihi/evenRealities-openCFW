/* SPDX-License-Identifier: MIT
 * Source ownership for the zero-table application state. The linker places
 * every object at its independently recovered stock RAM address.
 */
#include "ram_state.h"
#include "cy_scb_i2c.h"
#include "../eeprom/provider.h"

_Static_assert(sizeof(cy_stc_scb_i2c_context_t) == 84u, "SCB1 I2C context ABI");
_Static_assert(sizeof(touch_eeprom_context_layout) == 32u, "EEPROM context ABI");

#define TOUCH_BSS(name) __attribute__((section(".touch_bss." name), used))
volatile uint8_t touch_eeprom_ready_ram TOUCH_BSS("app_eeprom_ready");
uint8_t touch_eeprom_context_ram[32] TOUCH_BSS("app_eeprom_context");
volatile uint32_t touch_gesture_ticks_ram TOUCH_BSS("app_gesture_ticks");
uint8_t touch_i2c_context_ram[84] TOUCH_BSS("app_i2c_context");
uint8_t touch_gesture_state_ram[80] TOUCH_BSS("app_gesture_state");
uint8_t touch_report_ram[16] TOUCH_BSS("app_report");
uint8_t touch_i2c_rx_ram[16] TOUCH_BSS("app_i2c_rx");
uint8_t touch_i2c_tx_ram[16] TOUCH_BSS("app_i2c_tx");
volatile uint32_t touch_active_budget_ram TOUCH_BSS("app_active_budget");
volatile uint8_t touch_app_state_ram TOUCH_BSS("app_state");
volatile uint8_t touch_persist_ram TOUCH_BSS("app_persist");
volatile uint8_t touch_restart_ram TOUCH_BSS("app_restart");
volatile uint8_t touch_save_pending_ram TOUCH_BSS("app_save_pending");
touch_saved_record touch_saved_record_ram TOUCH_BSS("app_saved_record");
uint8_t touch_proximity_prior_ram[4] TOUCH_BSS("app_proximity_prior");
uint8_t touch_widget_processing_ram[24] TOUCH_BSS("app_widget_processing");
uint32_t touch_eeprom_provider_ram[12] TOUCH_BSS("app_eeprom_provider");
