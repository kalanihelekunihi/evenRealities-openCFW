#include <stdint.h>
uint32_t case_boot_transport_heap_allocate(uint32_t n){return n;}
void case_boot_heap_free(uint32_t x){(void)x;}
void case_boot_task_initialize(void (*a)(void*),const char*b,uint32_t c,void*d,uint32_t e,uint32_t*f,uint32_t g,uint32_t h){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;(void)h;}
void case_boot_task_register(uint32_t x){(void)x;}
uint32_t case_boot_task_create(void (*a)(void*),const char*b,uint32_t c,void*d,uint32_t e,uint32_t f,uint32_t g){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;return 0;}
