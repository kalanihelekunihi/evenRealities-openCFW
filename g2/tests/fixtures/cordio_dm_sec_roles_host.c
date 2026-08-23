#include <stdint.h>
#include <string.h>

struct open_cfw_dm_sec_role_ccb {
    uint8_t reserved0[12];
    uint16_t handle;
    uint8_t reserved14[2];
    uint8_t connection_id;
    uint8_t reserved17;
    uint8_t using_ltk;
    uint8_t reserved19[5];
    uint8_t temporary_security_level;
};

uint8_t open_cfw_test_dm_sec_roles_handler_id;
uint8_t open_cfw_test_dm_sec_roles_zero_key[16];
uint8_t open_cfw_test_dm_sec_roles_message[32];
uint8_t open_cfw_test_dm_sec_roles_start_random[8];
uint8_t open_cfw_test_dm_sec_roles_start_key[16];
struct open_cfw_dm_sec_role_ccb open_cfw_test_dm_sec_roles_ccb;
unsigned int open_cfw_test_dm_sec_roles_allocation;
unsigned int open_cfw_test_dm_sec_roles_alloc_calls;
unsigned int open_cfw_test_dm_sec_roles_alloc_size;
unsigned int open_cfw_test_dm_sec_roles_smp_send_calls;
unsigned int open_cfw_test_dm_sec_roles_wsf_send_calls;
unsigned int open_cfw_test_dm_sec_roles_copy_calls;
unsigned int open_cfw_test_dm_sec_roles_ccb_available;
unsigned int open_cfw_test_dm_sec_roles_start_calls;
uint8_t open_cfw_test_dm_sec_roles_send_handler;
uint16_t open_cfw_test_dm_sec_roles_start_handle;
uint16_t open_cfw_test_dm_sec_roles_start_diversifier;

void open_cfw_test_dm_sec_roles_reset(unsigned int allocation)
{
    memset(open_cfw_test_dm_sec_roles_message, 0xA5,
           sizeof(open_cfw_test_dm_sec_roles_message));
    memset(open_cfw_test_dm_sec_roles_start_random, 0,
           sizeof(open_cfw_test_dm_sec_roles_start_random));
    memset(open_cfw_test_dm_sec_roles_start_key, 0,
           sizeof(open_cfw_test_dm_sec_roles_start_key));
    memset(&open_cfw_test_dm_sec_roles_ccb, 0,
           sizeof(open_cfw_test_dm_sec_roles_ccb));
    open_cfw_test_dm_sec_roles_handler_id = 0x5AU;
    open_cfw_test_dm_sec_roles_allocation = allocation;
    open_cfw_test_dm_sec_roles_alloc_calls = 0U;
    open_cfw_test_dm_sec_roles_alloc_size = 0U;
    open_cfw_test_dm_sec_roles_smp_send_calls = 0U;
    open_cfw_test_dm_sec_roles_wsf_send_calls = 0U;
    open_cfw_test_dm_sec_roles_copy_calls = 0U;
    open_cfw_test_dm_sec_roles_ccb_available = 1U;
    open_cfw_test_dm_sec_roles_start_calls = 0U;
    open_cfw_test_dm_sec_roles_send_handler = 0U;
    open_cfw_test_dm_sec_roles_start_handle = 0U;
    open_cfw_test_dm_sec_roles_start_diversifier = 0U;
}

void *open_cfw_retained_cordio_wsf_msg_alloc(uint16_t size)
{
    open_cfw_test_dm_sec_roles_alloc_calls++;
    open_cfw_test_dm_sec_roles_alloc_size = size;
    return open_cfw_test_dm_sec_roles_allocation != 0U
        ? open_cfw_test_dm_sec_roles_message : 0;
}

void open_cfw_retained_cordio_smp_dm_msg_send(void *message)
{
    (void)message;
    open_cfw_test_dm_sec_roles_smp_send_calls++;
}

void open_cfw_retained_cordio_wsf_msg_send(
    uint8_t handler_id, void *message)
{
    (void)message;
    open_cfw_test_dm_sec_roles_wsf_send_calls++;
    open_cfw_test_dm_sec_roles_send_handler = handler_id;
}

void open_cfw_retained_cordio_calc128_copy(
    uint8_t destination[16], const uint8_t source[16])
{
    open_cfw_test_dm_sec_roles_copy_calls++;
    memcpy(destination, source, 16U);
}

struct open_cfw_dm_sec_role_ccb *
open_cfw_retained_cordio_dm_conn_ccb_by_id(uint8_t connection_id)
{
    (void)connection_id;
    return open_cfw_test_dm_sec_roles_ccb_available != 0U
        ? &open_cfw_test_dm_sec_roles_ccb : 0;
}

void open_cfw_retained_cordio_hci_le_start_encryption(
    uint16_t handle, const uint8_t random[8], uint16_t diversifier,
    const uint8_t key[16])
{
    open_cfw_test_dm_sec_roles_start_calls++;
    open_cfw_test_dm_sec_roles_start_handle = handle;
    open_cfw_test_dm_sec_roles_start_diversifier = diversifier;
    memcpy(open_cfw_test_dm_sec_roles_start_random, random, 8U);
    memcpy(open_cfw_test_dm_sec_roles_start_key, key, 16U);
}

void open_cfw_iar_memcpy_void(
    void *destination, const void *source, uint32_t size)
{
    open_cfw_test_dm_sec_roles_copy_calls++;
    memcpy(destination, source, size);
}
