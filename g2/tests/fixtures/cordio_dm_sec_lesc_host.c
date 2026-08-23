#include "cordio_dm_sec_lesc_host.h"

#include <stddef.h>
#include <stdint.h>
#include <string.h>

uint8_t open_cfw_test_dm_handler_id;
uint8_t open_cfw_test_dm_local_key[96];
uint8_t *open_cfw_test_dm_oob_random;
unsigned int open_cfw_test_dm_callback_calls;
unsigned int open_cfw_test_dm_free_calls;
unsigned int open_cfw_test_dm_copy_calls;
unsigned int open_cfw_test_dm_ecc_calls;
unsigned int open_cfw_test_dm_alloc_calls;
unsigned int open_cfw_test_dm_cancel_calls;
unsigned int open_cfw_test_dm_send_calls;
uint8_t open_cfw_test_dm_ecc_handler;
uint8_t open_cfw_test_dm_ecc_event;
uint8_t open_cfw_test_dm_cancel_connection;
uint8_t open_cfw_test_dm_cancel_reason;
uint8_t open_cfw_test_dm_callback_record[36];
uint8_t open_cfw_test_dm_message[22];
void *open_cfw_test_dm_free_values[2];
void *open_cfw_test_dm_sent_message;
void *open_cfw_test_dm_interface;

static unsigned int open_cfw_test_dm_allocation_success;
static void *open_cfw_test_dm_input_message;
static uint8_t *open_cfw_test_dm_input_ciphertext;
static uint8_t *open_cfw_test_dm_input_plaintext;

void open_cfw_test_dm_reset(unsigned int allocation_success)
{
    open_cfw_test_dm_handler_id = 0x5AU;
    memset(open_cfw_test_dm_local_key, 0xA5, sizeof(open_cfw_test_dm_local_key));
    open_cfw_test_dm_oob_random = NULL;
    open_cfw_test_dm_callback_calls = 0U;
    open_cfw_test_dm_free_calls = 0U;
    open_cfw_test_dm_copy_calls = 0U;
    open_cfw_test_dm_ecc_calls = 0U;
    open_cfw_test_dm_alloc_calls = 0U;
    open_cfw_test_dm_cancel_calls = 0U;
    open_cfw_test_dm_send_calls = 0U;
    open_cfw_test_dm_ecc_handler = 0U;
    open_cfw_test_dm_ecc_event = 0U;
    open_cfw_test_dm_cancel_connection = 0U;
    open_cfw_test_dm_cancel_reason = 0U;
    memset(open_cfw_test_dm_callback_record, 0xA5,
           sizeof(open_cfw_test_dm_callback_record));
    memset(open_cfw_test_dm_message, 0xA5, sizeof(open_cfw_test_dm_message));
    open_cfw_test_dm_free_values[0] = NULL;
    open_cfw_test_dm_free_values[1] = NULL;
    open_cfw_test_dm_sent_message = NULL;
    open_cfw_test_dm_interface = NULL;
    open_cfw_test_dm_allocation_success = allocation_success;
    open_cfw_test_dm_input_message = NULL;
    open_cfw_test_dm_input_ciphertext = NULL;
    open_cfw_test_dm_input_plaintext = NULL;
}

void open_cfw_test_dm_set_message_fields(
    void *message, uint8_t *ciphertext, uint8_t *plaintext)
{
    open_cfw_test_dm_input_message = message;
    open_cfw_test_dm_input_ciphertext = ciphertext;
    open_cfw_test_dm_input_plaintext = plaintext;
}

void open_cfw_test_dm_callback(void *message)
{
    ++open_cfw_test_dm_callback_calls;
    memcpy(open_cfw_test_dm_callback_record, message,
           sizeof(open_cfw_test_dm_callback_record));
}

uint8_t *open_cfw_test_dm_ciphertext(void *message)
{
    return message == open_cfw_test_dm_input_message
        ? open_cfw_test_dm_input_ciphertext : NULL;
}

uint8_t *open_cfw_test_dm_plaintext(void *message)
{
    return message == open_cfw_test_dm_input_message
        ? open_cfw_test_dm_input_plaintext : NULL;
}

void open_cfw_test_dm_set_interface(void *value)
{
    open_cfw_test_dm_interface = value;
}

void open_cfw_retained_cordio_wsf_buf_free(void *buffer)
{
    if (open_cfw_test_dm_free_calls < 2U) {
        open_cfw_test_dm_free_values[open_cfw_test_dm_free_calls] = buffer;
    }
    ++open_cfw_test_dm_free_calls;
}

void open_cfw_retained_cordio_calc128_copy(
    uint8_t destination[16], const uint8_t source[16])
{
    ++open_cfw_test_dm_copy_calls;
    memcpy(destination, source, 16U);
}

unsigned int open_cfw_retained_cordio_sec_ecc_gen_key(
    uint8_t handler_id, uint16_t parameter, uint8_t event)
{
    ++open_cfw_test_dm_ecc_calls;
    open_cfw_test_dm_ecc_handler = handler_id;
    open_cfw_test_dm_ecc_event = event;
    return parameter;
}

void open_cfw_iar_memcpy_void(
    void *destination, const void *source, uint32_t size)
{
    memcpy(destination, source, size);
}

void *open_cfw_retained_cordio_wsf_msg_alloc(uint16_t size)
{
    ++open_cfw_test_dm_alloc_calls;
    return open_cfw_test_dm_allocation_success != 0U && size == 22U
        ? open_cfw_test_dm_message : NULL;
}

void open_cfw_retained_cordio_smp_cancel_with_reattempt(
    uint8_t connection_id, void *message, uint8_t reason)
{
    uint8_t *header = (uint8_t *)message;
    ++open_cfw_test_dm_cancel_calls;
    open_cfw_test_dm_cancel_connection = connection_id;
    open_cfw_test_dm_cancel_reason = reason;
    header[2] = 0xEEU;
}

void open_cfw_retained_cordio_smp_dm_msg_send(void *message)
{
    ++open_cfw_test_dm_send_calls;
    open_cfw_test_dm_sent_message = message;
}
