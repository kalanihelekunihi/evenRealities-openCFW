#include <stdint.h>
uint32_t case_policy_sensor_shutdown(uint32_t x){return x;}
uint32_t case_boot_sensor_open(uint32_t x){return x;}
uint32_t case_boot_sensor_set_mode(uint32_t a,uint32_t b){return a+b;}
uint32_t case_boot_sensor_set_clock(uint32_t a,uint32_t b){return a+b;}
uint32_t case_boot_sensor_start(uint32_t x){return x;}
__attribute__((noreturn)) void case_boot_init_failure(void){for(;;);}
