#include <stdint.h>
uint32_t case_boot_transport_aging_status(void){return 0;}
uint32_t case_policy_log(uint32_t x){return x;}
uint32_t case_policy_log_number(uint32_t x,uint32_t y){return x+y;}
uint32_t case_legacy_logger(const char *s,...){return (uint32_t)(uintptr_t)s;}
int32_t case_boot_sensor_finish_signal(uint32_t a,uint32_t b){return (int32_t)(a+b);}
