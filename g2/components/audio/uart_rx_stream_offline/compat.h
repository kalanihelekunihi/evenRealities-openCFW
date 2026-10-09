#ifndef UART_RX_STREAM_COMPAT
#define UART_RX_STREAM_COMPAT
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
typedef int32_t BaseType_t;typedef uint32_t UBaseType_t;typedef void *TaskHandle_t;
typedef struct {volatile size_t xTail,xHead;size_t xLength,xTriggerLevelBytes;volatile TaskHandle_t xTaskWaitingToReceive,xTaskWaitingToSend;uint8_t *pucBuffer;uint8_t ucFlags;uint8_t pad[3];UBaseType_t uxStreamBufferNumber;} StreamBuffer_t;
typedef StreamBuffer_t *StreamBufferHandle_t;
typedef void (*StreamBufferCallbackFunction_t)(StreamBufferHandle_t,BaseType_t,BaseType_t *);
#define configUSE_TRACE_FACILITY 1
#define configUSE_SB_COMPLETED_CALLBACK 0
#define configASSERT_DEFINED 1
#define configMESSAGE_BUFFER_LENGTH_TYPE uint32_t
#define pdTRUE 1
#define pdFALSE 0
#define sbFLAGS_IS_MESSAGE_BUFFER 1u
#define sbBYTES_TO_STORE_MESSAGE_LENGTH 4u
#define configMIN(a,b) ((a)<(b)?(a):(b))
#define configASSERT(x) do{if(!(x))offline_assert();}while(0)
#define mtCOVERAGE_TEST_MARKER() ((void)0)
#define traceSTREAM_BUFFER_CREATE(a,b) ((void)0)
#define traceSTREAM_BUFFER_CREATE_FAILED(a) ((void)0)
#define traceSTREAM_BUFFER_SEND_FROM_ISR(a,b) ((void)0)
#define portSET_INTERRUPT_MASK_FROM_ISR() offline_mask_set()
#define portCLEAR_INTERRUPT_MASK_FROM_ISR(x) offline_mask_restore(x)
#define prvSEND_COMPLETE_FROM_ISR(s,w) do {UBaseType_t saved=offline_mask_set();if((s)->xTaskWaitingToReceive){offline_notify((s)->xTaskWaitingToReceive,0,0,0,NULL,(w));(s)->xTaskWaitingToReceive=NULL;}offline_mask_restore(saved);}while(0)
#define memcpy offline_copy
#define memset offline_fill
void *offline_copy(void *,const void *,size_t);void *offline_fill(void *,int,size_t);
void offline_assert(void) __attribute__((noreturn));
UBaseType_t offline_mask_set(void);void offline_mask_restore(UBaseType_t);
BaseType_t offline_notify(TaskHandle_t,UBaseType_t,uint32_t,uint32_t,uint32_t *,BaseType_t *);
void *pvPortMalloc(size_t);
size_t xStreamBufferSpacesAvailable(StreamBufferHandle_t);
static size_t prvWriteMessageToBuffer(StreamBuffer_t * const,const void *,size_t,size_t,size_t);
static size_t prvWriteBytesToBuffer(StreamBuffer_t * const,const uint8_t *,size_t,size_t);
static size_t prvBytesInBuffer(const StreamBuffer_t * const);
static void prvInitialiseNewStreamBuffer(StreamBuffer_t * const,uint8_t * const,size_t,size_t,uint8_t,StreamBufferCallbackFunction_t,StreamBufferCallbackFunction_t);
_Static_assert(sizeof(StreamBuffer_t)==36,"stock stream control");
#define AM_HAL_STATUS_SUCCESS 0u
#define AM_HAL_UART_STATUS_BUS_ERROR 0x8000000u
#define _VAL2FLD(field,value) ((value)<<field##_Pos)
#define UART0_DR_OEDATA_Pos 11u
#define UART0_DR_BEDATA_Pos 10u
#define UART0_DR_PEDATA_Pos 9u
#define UART0_DR_FEDATA_Pos 8u
#define UART0_DR_OEDATA_ERR 1u
#define UART0_DR_BEDATA_ERR 1u
#define UART0_DR_PEDATA_ERR 1u
#define UART0_DR_FEDATA_ERR 1u
typedef struct {uint8_t pad[40];uint32_t ui32Module;} am_hal_uart_state_t;
typedef struct {uint32_t DR,other[5];union {uint32_t FR;struct {uint32_t reserved:4,RXFE:1,TXFF:1,other:26;}FR_b;};} UartRegs;
#define UARTn(n) ((volatile UartRegs *)(0x40039000u+0x1000u*(n)))
#endif
