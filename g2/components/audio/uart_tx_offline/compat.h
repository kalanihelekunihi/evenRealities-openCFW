#ifndef UART_TX_OFFLINE_COMPAT
#define UART_TX_OFFLINE_COMPAT
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#define AM_HAL_STATUS_SUCCESS 0u
#define AM_REG_UART_NUM_MODULES 4u
#define AM_HAL_MAGIC_UART 0xea9e06u
#define AM_HAL_STATUS_OUT_OF_RANGE 5u
#define AM_HAL_STATUS_INVALID_ARG 6u
#define AM_HAL_STATUS_INVALID_OPERATION 7u
#define AM_HAL_STATUS_INVALID_HANDLE 2u
#define AM_HAL_UART_CHK_HANDLE(h) ((h) && ((*(uint32_t *)(h)&0x1ffffffu)==0x1ea9e06u))
#define AM_HAL_STATUS_TIMEOUT 4u
#define AM_HAL_UART_STATUS_TX_CHANNEL_BUSY 0x8000004u
#define AM_HAL_UART_WAIT_FOREVER 0xffffffffu
#define AM_CRITICAL_BEGIN uint32_t saved; __asm volatile("mrs %0, primask\ncpsid i":"=r"(saved)::"memory");
#define AM_CRITICAL_END __asm volatile("msr primask, %0"::"r"(saved):"memory");
typedef struct {uint32_t ui32WriteIndex,ui32ReadIndex,ui32Length,ui32Capacity,ui32ItemSize;uint8_t *pui8Data;} am_hal_queue_t;
#define am_hal_queue_data_left(q) ((q)->ui32Length)
#define am_hal_queue_space_left(q) ((q)->ui32Capacity-(q)->ui32Length)
typedef void (*am_hal_uart_callback_t)(uint32_t,void *);
typedef struct {uint8_t *pui8Data;uint32_t ui32NumBytes;uint32_t *pui32BytesTransferred;uint32_t ui32TimeoutMs;am_hal_uart_callback_t pfnCallback;void *pvContext;uint32_t ui32ErrorStatus;uint32_t *pui32TxBuffer,*pui32RxBuffer;uint32_t ui32FdRxNumBytes;uint32_t *pui32FdRxBytesTransferred;am_hal_uart_callback_t pfnFdRxCallback;void *pvFdRxContext;uint8_t eType,eDirection,ui8Priority,pad;} am_hal_uart_transfer_t;
typedef union {uint32_t word;struct {uint32_t magic:24,bInit:1,other:7;}s;} Prefix;
typedef struct {Prefix prefix;struct {bool bValid;uint8_t rest[35];}sRegState;uint32_t ui32Module;uint32_t psDmaQueue,ui32BaudRate;am_hal_queue_t sTxQueue,sRxQueue;am_hal_uart_transfer_t sActiveRead;uint32_t ui32BytesRead;am_hal_uart_transfer_t sActiveWrite;volatile uint32_t ui32BytesWritten;bool bEnableTxQueue,bEnableRxQueue,bLastTxComplete;uint8_t pad223[58];bool bCurrentlyWriting,bCurrentlyReading;uint8_t pad283;} am_hal_uart_state_t;
#define g_am_hal_uart_states ((am_hal_uart_state_t *)0x2006a02c)
_Static_assert(sizeof(am_hal_uart_state_t)==284,"stock handle stride");
typedef struct {uint32_t DR;uint32_t other[5];union {uint32_t FR;struct {uint32_t reserved:5,TXFF:1,other:26;}FR_b;};} UartRegs;
#define UARTn(n) ((volatile UartRegs *)(0x40039000u+0x1000u*(n)))
_Static_assert(sizeof(am_hal_uart_transfer_t)==56,"stock transfer size");
_Static_assert(offsetof(am_hal_uart_state_t,sTxQueue)==0x34,"stock queue");
_Static_assert(offsetof(am_hal_uart_state_t,sActiveWrite)==0xa0,"stock transaction");
_Static_assert(offsetof(am_hal_uart_state_t,bCurrentlyWriting)==0x119,"stock writing flag");
void am_hal_queue_init(am_hal_queue_t *,void *,uint32_t,uint32_t);
bool am_hal_queue_item_add(am_hal_queue_t *,const void *,uint32_t);
bool am_hal_queue_item_get(am_hal_queue_t *,void *,uint32_t);
void am_hal_delay_us(uint32_t);
uint32_t write_transaction_save(am_hal_uart_state_t *,const am_hal_uart_transfer_t *);
uint32_t am_hal_uart_fifo_write(void *,uint8_t *,uint32_t,uint32_t *);
static uint32_t tx_queue_update(void *);
static void nonblocking_write_sm(void *);
static uint32_t nonblocking_write(void *,const am_hal_uart_transfer_t *);
#endif
