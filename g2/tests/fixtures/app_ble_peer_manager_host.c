#include "app_ble_peer_manager_host.h"

#include <stddef.h>

enum {
    OPEN_CFW_TEST_PEER_EVENT_AUTH = 1,
    OPEN_CFW_TEST_PEER_EVENT_RESET = 2,
    OPEN_CFW_TEST_PEER_EVENT_REMOVE = 3,
    OPEN_CFW_TEST_PEER_EVENT_TARGET = 4,
    OPEN_CFW_TEST_PEER_EVENT_UNPAIR_ADDR = 5,
    OPEN_CFW_TEST_PEER_EVENT_UNPAIR_CONN = 6,
};

uint8_t open_cfw_test_peer_pending[7];
uint8_t open_cfw_test_peer_records[144];
uint8_t open_cfw_test_peer_addresses[256][6];
uint8_t open_cfw_test_peer_address_valid[256];
uint8_t open_cfw_test_peer_active_connection;
uint8_t open_cfw_test_peer_target[8];
uint8_t open_cfw_test_peer_target_connect;
uint8_t open_cfw_test_peer_unpair_connection;
uint8_t open_cfw_test_peer_unpair_address[7];
uintptr_t open_cfw_test_peer_removed_callbacks[2];
unsigned int open_cfw_test_peer_event_count;
unsigned int open_cfw_test_peer_events[8];
unsigned int open_cfw_test_peer_find_calls;
unsigned int open_cfw_test_peer_compare_calls;
unsigned int open_cfw_test_peer_auth_mode_calls;
unsigned int open_cfw_test_peer_reset_calls;
unsigned int open_cfw_test_peer_remove_calls;
unsigned int open_cfw_test_peer_set_target_calls;
unsigned int open_cfw_test_peer_unpair_addr_calls;
unsigned int open_cfw_test_peer_unpair_conn_calls;

static void open_cfw_test_peer_event(unsigned int event)
{
    open_cfw_test_peer_events[open_cfw_test_peer_event_count++] = event;
}

void open_cfw_test_peer_reset(void)
{
    unsigned int index;
    unsigned int octet;

    for (index = 0U; index < 7U; ++index) {
        open_cfw_test_peer_pending[index] = 0U;
        open_cfw_test_peer_unpair_address[index] = 0U;
    }
    for (index = 0U; index < 144U; ++index) {
        open_cfw_test_peer_records[index] = 0U;
    }
    for (index = 0U; index < 256U; ++index) {
        open_cfw_test_peer_address_valid[index] = 0U;
        for (octet = 0U; octet < 6U; ++octet) {
            open_cfw_test_peer_addresses[index][octet] = 0U;
        }
    }
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_peer_target[index] = 0U;
        open_cfw_test_peer_events[index] = 0U;
    }
    open_cfw_test_peer_active_connection = 0U;
    open_cfw_test_peer_target_connect = UINT8_MAX;
    open_cfw_test_peer_unpair_connection = 0U;
    open_cfw_test_peer_removed_callbacks[0] = 0U;
    open_cfw_test_peer_removed_callbacks[1] = 0U;
    open_cfw_test_peer_event_count = 0U;
    open_cfw_test_peer_find_calls = 0U;
    open_cfw_test_peer_compare_calls = 0U;
    open_cfw_test_peer_auth_mode_calls = 0U;
    open_cfw_test_peer_reset_calls = 0U;
    open_cfw_test_peer_remove_calls = 0U;
    open_cfw_test_peer_set_target_calls = 0U;
    open_cfw_test_peer_unpair_addr_calls = 0U;
    open_cfw_test_peer_unpair_conn_calls = 0U;
}

const uint8_t *open_cfw_test_peer_addr(uint8_t connection_id)
{
    ++open_cfw_test_peer_find_calls;
    if (open_cfw_test_peer_address_valid[connection_id] == 0U) {
        return NULL;
    }
    return open_cfw_test_peer_addresses[connection_id];
}

int open_cfw_test_peer_cmp(const uint8_t *left, const uint8_t *right)
{
    unsigned int index;

    ++open_cfw_test_peer_compare_calls;
    for (index = 0U; index < 6U; ++index) {
        if (left[index] != right[index]) {
            return 0;
        }
    }
    return 1;
}

uint8_t open_cfw_test_peer_active_conn_id(void)
{
    return open_cfw_test_peer_active_connection;
}

void open_cfw_test_peer_auth_mode_set(uint8_t mode)
{
    (void)mode;
    ++open_cfw_test_peer_auth_mode_calls;
    open_cfw_test_peer_event(OPEN_CFW_TEST_PEER_EVENT_AUTH);
}

void open_cfw_test_peer_reset_retry(void)
{
    ++open_cfw_test_peer_reset_calls;
    open_cfw_test_peer_event(OPEN_CFW_TEST_PEER_EVENT_RESET);
}

void open_cfw_test_peer_remove_delayed(void *callback)
{
    open_cfw_test_peer_removed_callbacks[open_cfw_test_peer_remove_calls++] =
        (uintptr_t)callback;
    open_cfw_test_peer_event(OPEN_CFW_TEST_PEER_EVENT_REMOVE);
}

void open_cfw_test_peer_set_target(
    const uint8_t *address, const char *name, uint8_t connect
)
{
    unsigned int index;

    (void)name;
    ++open_cfw_test_peer_set_target_calls;
    open_cfw_test_peer_target_connect = connect;
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_peer_target[index] = address[index];
    }
    open_cfw_test_peer_event(OPEN_CFW_TEST_PEER_EVENT_TARGET);
}

void open_cfw_test_peer_unpair_addr(const uint8_t *peer)
{
    unsigned int index;

    ++open_cfw_test_peer_unpair_addr_calls;
    for (index = 0U; index < 7U; ++index) {
        open_cfw_test_peer_unpair_address[index] = peer[index];
    }
    open_cfw_test_peer_event(OPEN_CFW_TEST_PEER_EVENT_UNPAIR_ADDR);
}

void open_cfw_test_peer_unpair_conn(uint8_t connection_id)
{
    ++open_cfw_test_peer_unpair_conn_calls;
    open_cfw_test_peer_unpair_connection = connection_id;
    open_cfw_test_peer_event(OPEN_CFW_TEST_PEER_EVENT_UNPAIR_CONN);
}
