#include <stdint.h>

extern uint8_t host_s200_reset_storage[16];
void open_cfw_retained_s200_startup_handoff(void);
#define OPEN_CFW_S200_MAIN_RESET_STATE \
    (*(volatile open_cfw_s200_reset_state *)host_s200_reset_storage)
#define OPEN_CFW_S200_MAIN_CLASS_DESCRIPTOR ((const void *)0x1234U)
#define OPEN_CFW_S200_MAIN_RELEASE_PATH "release"
#define OPEN_CFW_S200_MAIN_RELEASE_TYPE "V1.0.0"
#define OPEN_CFW_S200_MAIN_RELEASE_VERSION "2.2.6.10"
#define OPEN_CFW_S200_MAIN_STARTUP_HANDOFF() \
    open_cfw_retained_s200_startup_handoff()
