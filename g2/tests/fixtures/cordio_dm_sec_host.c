#include "cordio_dm_sec_host.h"

#include <stddef.h>
#include <stdint.h>
#include <string.h>

struct open_cfw_dm_sec_ccb {
    uint8_t reserved0[12];
    uint16_t handle;
    uint8_t reserved14[2];
    uint8_t connection_id;
    uint8_t reserved17;
    uint8_t using_ltk;
    uint8_t reserved19[4];
    uint8_t security_level;
    uint8_t temporary_security_level;
};

uint8_t *open_cfw_test_dm_sec_local_irk;
uint8_t *open_cfw_test_dm_sec_local_csrk;
uint8_t open_cfw_test_dm_sec_zero_key[16];
open_cfw_dm_sec_att_callback open_cfw_test_dm_sec_att_callback_value;
struct open_cfw_dm_sec_ccb open_cfw_test_dm_sec_ccb;
uint8_t open_cfw_test_dm_sec_allocated_message[32];
uint8_t open_cfw_test_dm_sec_dm_callback_record[32];
uint8_t open_cfw_test_dm_sec_att_callback_record[32];
uint8_t open_cfw_test_dm_sec_encrypt_record[32];
uint8_t open_cfw_test_dm_sec_reply_key[16];
uint8_t open_cfw_test_dm_sec_start_random[8];
uint8_t open_cfw_test_dm_sec_start_key[16];
uint8_t *open_cfw_test_dm_sec_stk;
void *open_cfw_test_dm_sec_interface;
void *open_cfw_test_dm_sec_sent_message;
unsigned int open_cfw_test_dm_sec_dm_callback_calls;
unsigned int open_cfw_test_dm_sec_att_callback_calls;
unsigned int open_cfw_test_dm_sec_set_idle_calls;
unsigned int open_cfw_test_dm_sec_reply_calls;
unsigned int open_cfw_test_dm_sec_negative_reply_calls;
unsigned int open_cfw_test_dm_sec_start_calls;
unsigned int open_cfw_test_dm_sec_encrypt_calls;
unsigned int open_cfw_test_dm_sec_alloc_calls;
unsigned int open_cfw_test_dm_sec_send_calls;
unsigned int open_cfw_test_dm_sec_db_init_calls;
uint8_t open_cfw_test_dm_sec_idle_connection;
uint8_t open_cfw_test_dm_sec_idle_mask;
uint8_t open_cfw_test_dm_sec_idle_value;
uint8_t open_cfw_test_dm_sec_stk_level;
unsigned int open_cfw_test_dm_sec_lesc_enabled;
uint16_t open_cfw_test_dm_sec_reply_handle;
uint16_t open_cfw_test_dm_sec_negative_handle;
uint16_t open_cfw_test_dm_sec_start_handle;
uint16_t open_cfw_test_dm_sec_start_diversifier;

static unsigned int open_cfw_test_dm_sec_by_handle;
static unsigned int open_cfw_test_dm_sec_by_id;
static unsigned int open_cfw_test_dm_sec_allocation_success;

static void open_cfw_test_dm_sec_att_callback(void *message)
{
    ++open_cfw_test_dm_sec_att_callback_calls;
    memcpy(open_cfw_test_dm_sec_att_callback_record, message, 8U);
}

void open_cfw_test_dm_sec_reset(unsigned int allocation_success)
{
    memset(&open_cfw_test_dm_sec_ccb, 0, sizeof(open_cfw_test_dm_sec_ccb));
    open_cfw_test_dm_sec_ccb.handle = 0x3456U;
    open_cfw_test_dm_sec_ccb.connection_id = 3U;
    memset(open_cfw_test_dm_sec_allocated_message, 0xA5,
           sizeof(open_cfw_test_dm_sec_allocated_message));
    memset(open_cfw_test_dm_sec_dm_callback_record, 0xA5,
           sizeof(open_cfw_test_dm_sec_dm_callback_record));
    memset(open_cfw_test_dm_sec_att_callback_record, 0xA5,
           sizeof(open_cfw_test_dm_sec_att_callback_record));
    memset(open_cfw_test_dm_sec_encrypt_record, 0xA5,
           sizeof(open_cfw_test_dm_sec_encrypt_record));
    memset(open_cfw_test_dm_sec_reply_key, 0xA5,
           sizeof(open_cfw_test_dm_sec_reply_key));
    memset(open_cfw_test_dm_sec_start_random, 0xA5,
           sizeof(open_cfw_test_dm_sec_start_random));
    memset(open_cfw_test_dm_sec_start_key, 0xA5,
           sizeof(open_cfw_test_dm_sec_start_key));
    memset(open_cfw_test_dm_sec_zero_key, 0, sizeof(open_cfw_test_dm_sec_zero_key));
    open_cfw_test_dm_sec_local_irk = (uint8_t *)(uintptr_t)0x11U;
    open_cfw_test_dm_sec_local_csrk = (uint8_t *)(uintptr_t)0x22U;
    open_cfw_test_dm_sec_att_callback_value = open_cfw_test_dm_sec_att_callback;
    open_cfw_test_dm_sec_stk = NULL;
    open_cfw_test_dm_sec_interface = NULL;
    open_cfw_test_dm_sec_sent_message = NULL;
    open_cfw_test_dm_sec_dm_callback_calls = 0U;
    open_cfw_test_dm_sec_att_callback_calls = 0U;
    open_cfw_test_dm_sec_set_idle_calls = 0U;
    open_cfw_test_dm_sec_reply_calls = 0U;
    open_cfw_test_dm_sec_negative_reply_calls = 0U;
    open_cfw_test_dm_sec_start_calls = 0U;
    open_cfw_test_dm_sec_encrypt_calls = 0U;
    open_cfw_test_dm_sec_alloc_calls = 0U;
    open_cfw_test_dm_sec_send_calls = 0U;
    open_cfw_test_dm_sec_db_init_calls = 0U;
    open_cfw_test_dm_sec_idle_connection = 0U;
    open_cfw_test_dm_sec_idle_mask = 0U;
    open_cfw_test_dm_sec_idle_value = 0U;
    open_cfw_test_dm_sec_stk_level = 0U;
    open_cfw_test_dm_sec_lesc_enabled = 0U;
    open_cfw_test_dm_sec_reply_handle = 0U;
    open_cfw_test_dm_sec_negative_handle = 0U;
    open_cfw_test_dm_sec_start_handle = 0U;
    open_cfw_test_dm_sec_start_diversifier = 0U;
    open_cfw_test_dm_sec_by_handle = 1U;
    open_cfw_test_dm_sec_by_id = 1U;
    open_cfw_test_dm_sec_allocation_success = allocation_success;
}

void open_cfw_test_dm_sec_set_ccb_presence(
    unsigned int by_handle, unsigned int by_id)
{
    open_cfw_test_dm_sec_by_handle = by_handle;
    open_cfw_test_dm_sec_by_id = by_id;
}

void open_cfw_test_dm_sec_set_stk(
    uint8_t *key, uint8_t security_level, unsigned int lesc_enabled)
{
    open_cfw_test_dm_sec_stk = key;
    open_cfw_test_dm_sec_stk_level = security_level;
    open_cfw_test_dm_sec_lesc_enabled = lesc_enabled;
}

void open_cfw_test_dm_sec_callback(void *message)
{
    ++open_cfw_test_dm_sec_dm_callback_calls;
    memcpy(open_cfw_test_dm_sec_dm_callback_record, message, 8U);
}

void open_cfw_test_dm_sec_set_interface(void *value)
{
    open_cfw_test_dm_sec_interface = value;
}

struct open_cfw_dm_sec_ccb *open_cfw_retained_cordio_dm_conn_ccb_by_handle(
    uint16_t handle)
{
    return open_cfw_test_dm_sec_by_handle != 0U && handle == 0x3456U
        ? &open_cfw_test_dm_sec_ccb : NULL;
}

struct open_cfw_dm_sec_ccb *open_cfw_retained_cordio_dm_conn_ccb_by_id(
    uint8_t connection_id)
{
    return open_cfw_test_dm_sec_by_id != 0U && connection_id == 3U
        ? &open_cfw_test_dm_sec_ccb : NULL;
}

int open_cfw_retained_iar_memcmp(
    const void *left, const void *right, uint32_t size)
{
    return memcmp(left, right, size);
}

uint8_t *open_cfw_retained_cordio_smp_dm_get_stk(
    uint8_t connection_id, uint8_t *security_level)
{
    if (connection_id != 3U) {
        return NULL;
    }
    *security_level = open_cfw_test_dm_sec_stk_level;
    return open_cfw_test_dm_sec_stk;
}

unsigned int open_cfw_retained_cordio_smp_dm_lesc_enabled(
    uint8_t connection_id)
{
    return connection_id == 3U ? open_cfw_test_dm_sec_lesc_enabled : 0U;
}

void open_cfw_retained_cordio_hci_le_ltk_request_reply(
    uint16_t handle, const uint8_t key[16])
{
    ++open_cfw_test_dm_sec_reply_calls;
    open_cfw_test_dm_sec_reply_handle = handle;
    memcpy(open_cfw_test_dm_sec_reply_key, key, 16U);
}

void open_cfw_retained_cordio_hci_le_ltk_request_negative_reply(
    uint16_t handle)
{
    ++open_cfw_test_dm_sec_negative_reply_calls;
    open_cfw_test_dm_sec_negative_handle = handle;
}

void open_cfw_retained_cordio_dm_conn_set_idle(
    uint8_t connection_id, uint8_t idle_mask, uint8_t idle_value)
{
    ++open_cfw_test_dm_sec_set_idle_calls;
    open_cfw_test_dm_sec_idle_connection = connection_id;
    open_cfw_test_dm_sec_idle_mask = idle_mask;
    open_cfw_test_dm_sec_idle_value = idle_value;
}

void open_cfw_retained_cordio_smp_dm_encrypt_indication(void *message)
{
    ++open_cfw_test_dm_sec_encrypt_calls;
    memcpy(open_cfw_test_dm_sec_encrypt_record, message, 8U);
}

void open_cfw_retained_cordio_hci_le_start_encryption(
    uint16_t handle, const uint8_t random[8], uint16_t diversifier,
    const uint8_t key[16])
{
    ++open_cfw_test_dm_sec_start_calls;
    open_cfw_test_dm_sec_start_handle = handle;
    open_cfw_test_dm_sec_start_diversifier = diversifier;
    memcpy(open_cfw_test_dm_sec_start_random, random, 8U);
    memcpy(open_cfw_test_dm_sec_start_key, key, 16U);
}

void *open_cfw_retained_cordio_wsf_msg_alloc(uint16_t size)
{
    ++open_cfw_test_dm_sec_alloc_calls;
    return open_cfw_test_dm_sec_allocation_success != 0U && size == 22U
        ? open_cfw_test_dm_sec_allocated_message : NULL;
}

void open_cfw_iar_memcpy_void(
    void *destination, const void *source, uint32_t size)
{
    memcpy(destination, source, size);
}

void open_cfw_retained_cordio_smp_dm_msg_send(void *message)
{
    ++open_cfw_test_dm_sec_send_calls;
    open_cfw_test_dm_sec_sent_message = message;
}

void open_cfw_retained_cordio_smp_db_init(void)
{
    ++open_cfw_test_dm_sec_db_init_calls;
}
