/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_EVEN_AI_TIMER_H
#define OPEN_CFW_EVEN_AI_TIMER_H

#include <stdint.h>

typedef struct {
    uint32_t start_tick;
    uint32_t duration_ticks;
    uint8_t state;
    uint8_t armed;
    uint8_t reserved[2];
} open_cfw_even_ai_timer_record;

void open_cfw_even_ai_common_timer_mgr_deinit(void);
void open_cfw_even_ai_common_timer_mgr_start(uint32_t duration_ticks);
void open_cfw_even_ai_common_timer_mgr_stop(void);
int open_cfw_even_ai_common_timer_mgr_check_timeout(void);
void open_cfw_even_ai_common_timer_mgr_process_timeout(void);

void open_cfw_even_ai_heartbeat_timer_mgr_deinit(void);
void open_cfw_even_ai_heartbeat_timer_mgr_start(uint32_t duration_ticks);
void open_cfw_even_ai_heartbeat_timer_mgr_stop(void);
int open_cfw_even_ai_heartbeat_timer_mgr_check_timeout(void);
void open_cfw_even_ai_heartbeat_timer_mgr_process_timeout(void);

void open_cfw_even_ai_timer_deinit_all(void);
void open_cfw_even_ai_timer_start_all(uint32_t common_duration_ticks);
void open_cfw_even_ai_timer_process_all(void);

#endif
