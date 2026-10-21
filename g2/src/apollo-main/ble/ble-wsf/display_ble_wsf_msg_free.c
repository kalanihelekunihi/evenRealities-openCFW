/* Native WsfMsgFree 0x4bf9b0; pinned Cordio wsf_msg.c confirms 8-byte header. */
#include <stdint.h>
extern void WsfBufFree(void *block);
void WsfMsgFree(void *message) {
    WsfBufFree((uint8_t *)message - 8u);
}
