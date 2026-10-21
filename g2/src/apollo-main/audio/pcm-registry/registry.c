#include "registry.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define D(n,a) uint32_t pcm_registry_##n(void){if(W(a)){uint32_t(*f)(void)=(void*)(uintptr_t)W(a);return f();}return 0;}
D(before_override,0x20073284u)
D(before_enable,0x20073288u)
D(after_enable,0x2007328cu)
D(ton_initialize,0x20073290u)
D(tempco_suspend,0x20073298u)
D(lp_initialize,0x200732a0u)
D(lp_enable,0x200732a4u)
D(lp_disable,0x200732a8u)
