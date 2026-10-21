/* Native WsfQueueEnq 0x538c24 and WsfCsEnter/Exit 0x52b8a4/b6. */
#include <stdint.h>
extern volatile uint8_t audio_wsf_cs_depth; /* live RAM */
void WsfCsEnter(void) {
    if(audio_wsf_cs_depth==0u)
        __asm volatile("cpsid i" ::: "memory");
    audio_wsf_cs_depth++;
}
void WsfCsExit(void) {
    audio_wsf_cs_depth--;
    if(audio_wsf_cs_depth==0u)
        __asm volatile("cpsie i" ::: "memory");
}
void WsfQueueEnq(void *queue,void *node) {
    uintptr_t *q=(uintptr_t *)queue;
    uintptr_t *next=(uintptr_t *)node;
    *next=0u;
    WsfCsEnter();
    if(q[0]==0u) {
        q[0]=(uintptr_t)node;
        q[1]=(uintptr_t)node;
    } else {
        *(uintptr_t *)q[1]=(uintptr_t)node;
        q[1]=(uintptr_t)node;
    }
    WsfCsExit();
}
