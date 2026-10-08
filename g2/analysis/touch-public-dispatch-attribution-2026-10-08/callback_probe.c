#include <stdint.h>
void touch_dispatch_probe(void *c){*(volatile uint32_t *)0x20009200=(uint32_t)(uintptr_t)c;(*(volatile uint32_t *)0x20009204)++;}
