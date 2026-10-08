/* Synthetic callbacks, not firmware behavior or an entry stub. */
#include <stdint.h>
typedef struct {void *base;uint32_t *context;} params;
uint32_t touch_pm_probe(params *p,uint32_t mode) {
 volatile uint32_t *log=(volatile uint32_t *)0x20003000u;
 uint32_t n=log[0]++;log[1+3*n]=p->context[0];log[2+3*n]=mode;log[3+3*n]=(uint32_t)p->base;
 return p->context[mode==1?1:2];
}
