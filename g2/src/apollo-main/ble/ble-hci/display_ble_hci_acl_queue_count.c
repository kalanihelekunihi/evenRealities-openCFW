/* Native WsfQueueCount 0x538cf6: count singly linked queue under WSF CS. */
#include <stdint.h>
extern void WsfCsEnter(void);
extern void WsfCsExit(void);
uint16_t WsfQueueCount(const void *queue){
    uint16_t count=0u;
    WsfCsEnter();
    const uint8_t *node=(const uint8_t *)(uintptr_t)*(const uint32_t *)queue;
    while(node!=0){
        count=(uint16_t)(count+1u);
        node=(const uint8_t *)(uintptr_t)*(const uint32_t *)(const void *)node;
    }
    WsfCsExit();
    return count;
}
