#include <string.h>

#include "charger_common_host.h"

open_cfw_test_charger_runtime_type open_cfw_test_charger_runtime;
open_cfw_test_charger_info_type open_cfw_test_charger_local_info;
open_cfw_test_charger_driver_type open_cfw_test_charger_driver;
void *open_cfw_test_charger_mutex;
uint8_t open_cfw_test_charger_role_value;
int open_cfw_test_charger_lock_result;
uint32_t open_cfw_test_charger_create_count;
uint32_t open_cfw_test_charger_delete_count;
uint32_t open_cfw_test_charger_lock_count;
uint32_t open_cfw_test_charger_unlock_count;
uint32_t open_cfw_test_charger_start_count;
uint32_t open_cfw_test_charger_stop_count;
uint32_t open_cfw_test_charger_send_count;
uint32_t open_cfw_test_charger_publish_count;
uint32_t open_cfw_test_charger_diagnostic_count;
uint16_t open_cfw_test_charger_last_service;
uint16_t open_cfw_test_charger_last_length;
uint8_t open_cfw_test_charger_last_message[12];
uint8_t open_cfw_test_charger_last_field;
int32_t open_cfw_test_charger_last_value;
uint32_t open_cfw_test_charger_last_diagnostic;

void *open_cfw_test_charger_create_mutex(void)
{
    ++open_cfw_test_charger_create_count;
    return (void *)(uintptr_t)0x1234u;
}

void open_cfw_test_charger_delete_mutex(void *mutex)
{
    (void)mutex;
    ++open_cfw_test_charger_delete_count;
}

int open_cfw_test_charger_lock_mutex(void *mutex, uint32_t timeout)
{
    (void)mutex;
    (void)timeout;
    ++open_cfw_test_charger_lock_count;
    return open_cfw_test_charger_lock_result;
}

void open_cfw_test_charger_unlock_mutex(void *mutex)
{
    (void)mutex;
    ++open_cfw_test_charger_unlock_count;
}

void open_cfw_test_charger_start_sync_timer(void)
{
    ++open_cfw_test_charger_start_count;
}

void open_cfw_test_charger_stop_sync_timer(void)
{
    ++open_cfw_test_charger_stop_count;
}

uint8_t open_cfw_test_charger_role(void)
{
    return open_cfw_test_charger_role_value;
}

void open_cfw_test_charger_send_message(
    uint16_t service, const void *message, uint16_t length, uint8_t flags
)
{
    (void)flags;
    ++open_cfw_test_charger_send_count;
    open_cfw_test_charger_last_service = service;
    open_cfw_test_charger_last_length = length;
    memcpy(open_cfw_test_charger_last_message, message, length);
}

void open_cfw_test_charger_publish(uint8_t field, int32_t value)
{
    ++open_cfw_test_charger_publish_count;
    open_cfw_test_charger_last_field = field;
    open_cfw_test_charger_last_value = value;
}

void open_cfw_test_charger_diagnostic(uint32_t code)
{
    ++open_cfw_test_charger_diagnostic_count;
    open_cfw_test_charger_last_diagnostic = code;
}

void open_cfw_test_charger_reset(void)
{
    memset(&open_cfw_test_charger_runtime, 0, sizeof(open_cfw_test_charger_runtime));
    memset(&open_cfw_test_charger_local_info, 0, sizeof(open_cfw_test_charger_local_info));
    memset(&open_cfw_test_charger_driver, 0, sizeof(open_cfw_test_charger_driver));
    open_cfw_test_charger_mutex = NULL;
    open_cfw_test_charger_role_value = 1u;
    open_cfw_test_charger_lock_result = 0;
    open_cfw_test_charger_create_count = 0;
    open_cfw_test_charger_delete_count = 0;
    open_cfw_test_charger_lock_count = 0;
    open_cfw_test_charger_unlock_count = 0;
    open_cfw_test_charger_start_count = 0;
    open_cfw_test_charger_stop_count = 0;
    open_cfw_test_charger_send_count = 0;
    open_cfw_test_charger_publish_count = 0;
    open_cfw_test_charger_diagnostic_count = 0;
    open_cfw_test_charger_last_service = 0;
    open_cfw_test_charger_last_length = 0;
    memset(open_cfw_test_charger_last_message, 0,
        sizeof(open_cfw_test_charger_last_message));
    open_cfw_test_charger_last_field = 0;
    open_cfw_test_charger_last_value = 0;
    open_cfw_test_charger_last_diagnostic = 0;
}
