/* Bounded projection of pinned Ambiq nonblocking_read_sm and rx_queue_update. */
#include "../uart-tx/compat.h"
extern uint32_t am_hal_uart_fifo_read(void *,uint8_t *,uint32_t,uint32_t *);
static uint32_t rx_queue_update_local(void *handle)
{
    am_hal_uart_state_t *s=(am_hal_uart_state_t *)handle;
    uint8_t data[32];uint32_t transferred=0;uint32_t status;
    AM_CRITICAL_BEGIN
    status=am_hal_uart_fifo_read(handle,data,32,&transferred);
    if (status==0 && !am_hal_queue_item_add(&s->sRxQueue,data,transferred)) status=0x08000001u;
    AM_CRITICAL_END
    return status;
}
void uart_irq_read_sm(void *handle)
{
    am_hal_uart_state_t *s=(am_hal_uart_state_t *)handle;
    if (s->bEnableRxQueue) (void)rx_queue_update_local(handle);
    if (s->bCurrentlyReading) {
        bool return_after=false;
        AM_CRITICAL_BEGIN
        uint32_t i=s->ui32BytesRead;
        uint32_t left=s->sActiveRead.ui32NumBytes-i;
        uint8_t *dst=&s->sActiveRead.pui8Data[i];
        uint32_t read_size=0;
        if (s->bEnableRxQueue) {
            uint32_t available=am_hal_queue_data_left(&s->sRxQueue);
            read_size=left<available?left:available;
            if (!am_hal_queue_item_get(&s->sRxQueue,dst,read_size)) {
                s->bCurrentlyReading=false;
                if (s->sActiveRead.pfnCallback) {
                    s->sActiveRead.pfnCallback(1,s->sActiveRead.pvContext);
                    return_after=true;
                }
            }
        } else {
            (void)am_hal_uart_fifo_read(handle,dst,left,&read_size);
        }
        if (!return_after) s->ui32BytesRead += read_size;
        AM_CRITICAL_END
        if (return_after) return;
        if (s->sActiveRead.pui32BytesTransferred)
            *s->sActiveRead.pui32BytesTransferred=s->ui32BytesRead;
        if (s->ui32BytesRead==s->sActiveRead.ui32NumBytes) {
            s->bCurrentlyReading=false;
            if (s->sActiveRead.pfnCallback)
                s->sActiveRead.pfnCallback(0,s->sActiveRead.pvContext);
        }
    }
}
