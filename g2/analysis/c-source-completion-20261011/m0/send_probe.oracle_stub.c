#include <stdint.h>
void case_policy_sensor_prepare(void){}
uint32_t case_policy_sensor_shutdown(uint32_t x){return x;}
void case_boot_sensor_service_start(void){}
void case_control_write(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void case_policy_ota_left_prepare(void){}
void case_policy_ota_right_prepare(void){}
int32_t case_policy_sensor_delay(uint32_t x){return (int32_t)x;}
uint32_t case_boot_sensor_send_packet(const uint8_t *p,uint32_t n){return (uint32_t)(uintptr_t)p+n;}
void case_boot_sensor_post_transmit(void){}
uint32_t case_boot_sensor_finish_guard(uint32_t a,const uint8_t*b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
void log_hex_buffer(const uint8_t*b,uint32_t n){(void)b;(void)n;}
uint32_t case_policy_sensor_divide(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}
uint32_t case_policy_log(uint32_t x){return x;}
uint32_t case_policy_log_number(uint32_t x,uint32_t y){return x+y;}
void case_policy_idle_clear(void){}
