#ifndef OPEN_CFW_TEST_CORDIO_DM_SEC_LESC_HOST_H
#define OPEN_CFW_TEST_CORDIO_DM_SEC_LESC_HOST_H

#include <stdint.h>

extern uint8_t open_cfw_test_dm_handler_id;
extern uint8_t open_cfw_test_dm_local_key[96];
extern uint8_t *open_cfw_test_dm_oob_random;

void open_cfw_test_dm_callback(void *message);
uint8_t *open_cfw_test_dm_ciphertext(void *message);
uint8_t *open_cfw_test_dm_plaintext(void *message);
void open_cfw_test_dm_set_interface(void *value);

#define OPEN_CFW_DM_SEC_LESC_CALLBACK(message) \
    open_cfw_test_dm_callback((message))
#define OPEN_CFW_DM_SEC_LESC_HANDLER_ID open_cfw_test_dm_handler_id
#define OPEN_CFW_DM_SEC_LESC_CIPHERTEXT(message) \
    open_cfw_test_dm_ciphertext((message))
#define OPEN_CFW_DM_SEC_LESC_PLAINTEXT(message) \
    open_cfw_test_dm_plaintext((message))
#define OPEN_CFW_DM_SEC_LESC_OOB_RANDOM open_cfw_test_dm_oob_random
#define OPEN_CFW_DM_SEC_LESC_LOCAL_KEY open_cfw_test_dm_local_key
#define OPEN_CFW_DM_SEC_LESC_SET_INTERFACE(value) \
    open_cfw_test_dm_set_interface((value))
#define OPEN_CFW_DM_SEC_LESC_INTERFACE ((void *)(uintptr_t)0x78A8A4U)

void open_cfw_test_dm_reset(unsigned int allocation_success);
void open_cfw_test_dm_set_message_fields(
    void *message, uint8_t *ciphertext, uint8_t *plaintext);

#endif
