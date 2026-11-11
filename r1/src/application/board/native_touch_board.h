#ifndef R1_NATIVE_TOUCH_BOARD_H
#define R1_NATIVE_TOUCH_BOARD_H
#include <stdint.h>
#include "native_touch_ready_state.h"
extern volatile uint8_t r1_touch_board_active;
uint32_t r1_touch_ready_callback_setter(uint32_t callback);
uint32_t r1_touch_ready_irq_callback(void);
uint32_t r1_touch_board_open(void);
uint32_t r1_touch_power_on_step(void);
uintptr_t r1_touch_pending_flag_consume(void);
#endif
