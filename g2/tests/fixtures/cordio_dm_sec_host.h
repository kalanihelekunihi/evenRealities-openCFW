#ifndef OPEN_CFW_TEST_CORDIO_DM_SEC_HOST_H
#define OPEN_CFW_TEST_CORDIO_DM_SEC_HOST_H

#include <stdint.h>

typedef void (*open_cfw_dm_sec_callback)(void *message);
typedef void (*open_cfw_dm_sec_att_callback)(void *message);

extern uint8_t *open_cfw_test_dm_sec_local_irk;
extern uint8_t *open_cfw_test_dm_sec_local_csrk;
extern uint8_t open_cfw_test_dm_sec_zero_key[16];
extern open_cfw_dm_sec_att_callback open_cfw_test_dm_sec_att_callback_value;

void open_cfw_test_dm_sec_callback(void *message);
void open_cfw_test_dm_sec_set_interface(void *value);

#define OPEN_CFW_DM_SEC_CALLBACK(message) \
    open_cfw_test_dm_sec_callback((message))
#define OPEN_CFW_DM_SEC_ATT_CALLBACK open_cfw_test_dm_sec_att_callback_value
#define OPEN_CFW_DM_SEC_SET_INTERFACE(value) \
    open_cfw_test_dm_sec_set_interface((value))
#define OPEN_CFW_DM_SEC_INTERFACE ((void *)(uintptr_t)0x78A898U)
#define OPEN_CFW_DM_SEC_LOCAL_IRK open_cfw_test_dm_sec_local_irk
#define OPEN_CFW_DM_SEC_LOCAL_CSRK open_cfw_test_dm_sec_local_csrk
#define OPEN_CFW_DM_SEC_ZERO_KEY open_cfw_test_dm_sec_zero_key

void open_cfw_test_dm_sec_reset(unsigned int allocation_success);
void open_cfw_test_dm_sec_set_ccb_presence(
    unsigned int by_handle, unsigned int by_id);
void open_cfw_test_dm_sec_set_stk(
    uint8_t *key, uint8_t security_level, unsigned int lesc_enabled);

#endif
