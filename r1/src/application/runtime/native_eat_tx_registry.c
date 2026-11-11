/* Stock 0x3d7fc and 0x3d7ac: TX callback slots and their default bindings. */
#include <stddef.h>
#include <stdint.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include "../board/native_task_construction.h"
#include "task.h"
#include "native_eat_command_table.h"

_Static_assert(sizeof(struct r1_eat_command_entry) == 16u,
               "stock EAT command entry size");

struct r1_eat_tx_registry {
    uint32_t flags;
    uint32_t reserved;
    uintptr_t command_table;
    uint32_t command_count;
    uint32_t tx_mask;
    uint32_t reserved_20;
    uintptr_t callbacks[3];
    char response[512];
};

_Static_assert(offsetof(struct r1_eat_tx_registry, response) == 36u,
               "stock EAT response buffer offset");
_Static_assert(offsetof(struct r1_eat_tx_registry, tx_mask) == 16u,
               "stock EAT TX mask offset");
_Static_assert(offsetof(struct r1_eat_tx_registry, callbacks) == 24u,
               "stock EAT TX callback offset");

volatile struct r1_eat_tx_registry r1_eat_tx_registry;

extern uint32_t r1_rtt_channel0_write_callback(const void *, uint32_t);
extern int32_t r1_ble_tx_type2_send(const void *, uint32_t);

void r1_tx_callback_register(uint32_t channel, uintptr_t callback)
{
    if (channel < 3u) {
        r1_eat_tx_registry.callbacks[channel] = callback;
        r1_eat_tx_registry.tx_mask |= UINT32_C(1) << channel;
    }
}

void r1_tx_callback_register_defaults(void)
{
    r1_tx_callback_register(
        1u, (uintptr_t)&r1_rtt_channel0_write_callback);
    r1_tx_callback_register(
        2u, (uintptr_t)&r1_ble_tx_type2_send);
}

/* Stock 0x4ef24: format once, then deliver to the selected TX slots. */
void r1_eat_respond_format(const char *format, ...)
{
    va_list arguments;
    va_start(arguments, format);
    const int length = vsnprintf((char *)r1_eat_tx_registry.response,
                                 sizeof r1_eat_tx_registry.response,
                                 format, arguments);
    va_end(arguments);
    if (length <= 0) {
        return;
    }

    const uint8_t mode = (uint8_t)r1_eat_tx_registry.reserved_20;
    if (mode == 0u) {
        for (uint32_t channel = 1u; channel < 3u; ++channel) {
            const uintptr_t callback = r1_eat_tx_registry.callbacks[channel];
            if ((r1_eat_tx_registry.tx_mask & (UINT32_C(1) << channel)) != 0u &&
                    callback != 0u) {
                ((void (*)(const void *, uint32_t))callback)(
                    (const void *)r1_eat_tx_registry.response, (uint32_t)length);
            }
        }
    } else if (mode == 2u &&
               (r1_eat_tx_registry.tx_mask & 4u) != 0u &&
               r1_eat_tx_registry.callbacks[2] != 0u) {
        ((void (*)(const void *, uint32_t))r1_eat_tx_registry.callbacks[2])(
            (const void *)r1_eat_tx_registry.response, (uint32_t)length);
    }
}

extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(
    uint32_t, const char *, const char *, ...);
extern void nrf_log_frontend_std_1(uint32_t, const char *, uint32_t);

/* Stock 0x4ef8c: publish the command table and enable core processing. */
void r1_eat_core_init(void)
{
    static const char ring[] = "[RING]====eAT core init[%d]====";
    static const char sdk[] = "====eAT core init[%d]====";
    r1_eat_tx_registry.command_table = (uintptr_t)r1_eat_command_table;
    r1_eat_tx_registry.command_count = 37u;
    r1_tx_callback_register_defaults();
    r1_eat_tx_registry.reserved = 0u;
    r1_eat_tx_registry.flags |= 3u;
    if ((r1_structured_log_mode_get() & 1u) ||
            (r1_structured_log_mode_get() & 4u)) {
        (void)r1_structured_log_format(0x0c400000u, ring, ring,
                                       r1_eat_tx_registry.command_count);
    }
    if (r1_structured_log_mode_get() & 2u) {
        nrf_log_frontend_std_1(0x001c0003u, sdk,
                               r1_eat_tx_registry.command_count);
    }
}

struct r1_eat_background_command {
    void (*callback)(char *);
    char *argument;
};

_Static_assert(sizeof(struct r1_eat_background_command) == 8u,
               "stock EAT background command size");

extern void *pvPortMalloc(size_t);
extern void vPortFree(void *);
extern TaskHandle_t xTaskGetCurrentTaskHandle(void);
extern void vTaskDelete(TaskHandle_t);

/* Stock 0x44ea0: run an asynchronous command, then delete this task. */
void r1_eat_background_command_thread(void *context)
{
    struct r1_eat_background_command *const command = context;
    if (command != NULL && command->callback != NULL) {
        command->callback(command->argument);
        vPortFree(command);
    }
    vTaskDelete(xTaskGetCurrentTaskHandle());
}

/* Stock 0x3d7cc: schedule a command in its own 1024-word AT task. */
void r1_eat_background_command_enqueue(
    void (*callback)(char *), char *argument)
{
    struct r1_eat_background_command *const command = pvPortMalloc(8u);
    if (command == NULL) {
        return;
    }
    command->callback = callback;
    command->argument = argument;
    (void)r1_native_task_create(
        r1_eat_background_command_thread, "AT", 1024u, command, 2u, NULL);
}

/* Stock 0x4f6f8. Its table is installed by the separate core initializer. */

void r1_eat_command_dispatch(char *name, char *argument)
{
    if ((r1_eat_tx_registry.flags & 3u) != 3u || name == NULL) {
        return;
    }
    const size_t length = strlen(name);
    if (length >= 30u) {
        return;
    }
    for (uint32_t index = 0u;
         index < r1_eat_tx_registry.command_count; ++index) {
        const volatile struct r1_eat_command_entry *const entry =
            (const volatile struct r1_eat_command_entry *)(uintptr_t)
            r1_eat_tx_registry.command_table + index;
        if (memcmp((const void *)entry->name, name, length) != 0) {
            continue;
        }
        if ((r1_eat_tx_registry.flags & 4u) != 0u &&
                (entry->flags & 1u) == 0u) {
            return;
        }
        void (*const callback)(char *) = entry->callback;
        if (callback == NULL) {
            continue;
        }
        if ((entry->flags & 2u) != 0u) {
            r1_eat_background_command_enqueue(callback, argument);
        } else {
            callback(argument);
        }
    }
}
