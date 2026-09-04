/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_THREAD_NOTIFICATION_H
#define OPEN_CFW_THREAD_NOTIFICATION_H

#include <stdint.h>

typedef struct {
    uint32_t reserved_0;
    uint32_t reserved_4;
    uint32_t thread_id;
    uint32_t queue_id;
} open_cfw_thread_notification_state;

typedef struct {
    uint32_t id;
    uint32_t payload_bytes;
    uint8_t payload[];
} open_cfw_thread_notification_record;

enum {
    OPEN_CFW_THREAD_NOTIFICATION_RECORD_WHITELIST = 4U,
    OPEN_CFW_THREAD_NOTIFICATION_RECORD_MESSAGE = 0x101U,
    OPEN_CFW_THREAD_NOTIFICATION_EVENT_WHITELIST = 0x00000002U,
    OPEN_CFW_THREAD_NOTIFICATION_EVENT_QUEUE = 0x00400000U,
    OPEN_CFW_THREAD_NOTIFICATION_EVENT_EXIT = 0x00800000U,
    OPEN_CFW_THREAD_NOTIFICATION_EVENT_MASK = 0x00FFFFFFU,
};

void open_cfw_thread_notification_entry(void *argument);
void open_cfw_thread_notification_init_hook(void);
void open_cfw_thread_notification_queue_init(void);
void open_cfw_thread_notification_whitelist_init(void);
void open_cfw_thread_notification_state_enter(void);
void open_cfw_thread_notification_state_ready(void);
void open_cfw_thread_notification_create(void);
void open_cfw_thread_notification_destroy(void);
void open_cfw_thread_notification_drain_queue(void);
void open_cfw_thread_notification_event_handler(uint32_t events);
_Noreturn void open_cfw_thread_notification_exit(void);
void open_cfw_thread_notification_send_event(uint32_t events);

#endif
