/* Explicit synthetic kernel result providers; not stock kernel reconstruction. */
#include <stdint.h>
#define CONFIG ((volatile uint32_t *)0x20003000u)
int32_t case_model_from_isr(void *id,uint32_t flags,int32_t *yield){(void)id;(void)flags;*yield=(int32_t)CONFIG[1];return (int32_t)CONFIG[0];}
uint32_t case_model_thread(void *id,uint32_t flags){(void)id;return CONFIG[2]|flags;}
uint32_t xEventGroupGetBitsFromISR(void *id){(void)id;return CONFIG[2];}
