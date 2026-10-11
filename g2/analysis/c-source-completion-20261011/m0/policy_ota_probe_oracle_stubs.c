#include <stdint.h>
/* Synthetic oracle-only data; no stock payload is copied. */
const uint8_t case_policy_ota_probe_template[12]={0xa5,0x5a,0xa5,0x5a,0xa5,0x5a,0xa5,0x5a,0xa5,0x5a,0xa5,0x5a};
__attribute__((noinline,used)) void case_policy_log(uint32_t x){(void)x;__asm__ volatile("nop");}
__attribute__((noinline,used)) void case_policy_wait(uint32_t x){(void)x;__asm__ volatile("nop");}
__attribute__((noinline,used)) void case_policy_send_probe(uint32_t x,const uint8_t *y,uint32_t z){(void)x;(void)y;(void)z;__asm__ volatile("nop");}
__attribute__((noinline,used)) void case_policy_parse_probe(uint32_t x){(void)x;__asm__ volatile("nop");}
