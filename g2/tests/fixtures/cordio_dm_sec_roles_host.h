#include <stdint.h>

extern uint8_t open_cfw_test_dm_sec_roles_handler_id;
extern uint8_t open_cfw_test_dm_sec_roles_zero_key[16];

#define OPEN_CFW_DM_SEC_ROLE_HANDLER_ID \
    open_cfw_test_dm_sec_roles_handler_id
#define OPEN_CFW_DM_SEC_ROLE_ZERO_KEY \
    ((const uint8_t *)open_cfw_test_dm_sec_roles_zero_key)
