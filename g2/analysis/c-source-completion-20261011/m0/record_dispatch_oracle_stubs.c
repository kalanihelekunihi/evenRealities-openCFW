#include <stdint.h>
void case_record_log(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t g){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;}
void case_record_hex_log(const uint8_t*a,uint32_t n){(void)a;(void)n;}
void case_record_forward(const uint8_t*a,uint32_t n){(void)a;(void)n;}
void case_record_copy_5a(uint8_t*d,const uint8_t*s,uint32_t n){for(uint32_t i=0;i<n;i++)d[i]=s[i];}
