#include <stdint.h>
extern unsigned char host_sec_state_storage[128];
#define OPEN_CFW_CORDIO_SEC_STATE (*(volatile sec_control *)host_sec_state_storage)
