#include <stdint.h>
uint32_t case_boot_transport_left_aging(uint32_t x){return x;}
uint32_t case_boot_transport_right_aging(uint32_t x){return x;}
uint32_t case_policy_service_idle(void){return 0;}
uint32_t case_policy_log(uint32_t x){return x;}
uint32_t case_legacy_logger(const char *s,...){return (uint32_t)(uintptr_t)s;}
__attribute__((noreturn)) void case_init_display_reset(void){for(;;);}
