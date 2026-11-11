/* Native structured-log routing/header construction (0x91638) and state
 * accessors (0x91864/0x590A0). Encode/transport remains a real provider. */
#include <stdint.h>
#include <stdarg.h>
#include "cmsis_gcc.h"
extern volatile uint8_t r1_structured_log_mode;
volatile uint8_t r1_structured_log_clock_state __attribute__((section(".r1.log.clock"),aligned(1)));
volatile uint8_t r1_structured_log_export_state __attribute__((section(".r1.log.export"),aligned(1)));
uint32_t r1_structured_log_clock_available(void) { return r1_structured_log_clock_state; }
uint32_t r1_structured_log_export_active(void) { return r1_structured_log_export_state; }
extern void vPortEnterCritical(void);
extern void vPortExitCritical(void);
extern void r1_structured_log_encode_format(uint32_t header,const char *format,va_list arguments);
extern void r1_structured_log_encode_typed(uint32_t header,va_list arguments);
uint32_t r1_structured_log_format(uint32_t marker,const char *descriptor,const char *format,...) {
    if ((r1_structured_log_mode & 4u) && !r1_structured_log_clock_available()) return 0;
    if ((r1_structured_log_mode & 1u) && r1_structured_log_export_active()) return 0;
    uint32_t saved=0;
    if (__get_IPSR()!=0) { saved=__get_BASEPRI();__set_BASEPRI(64); }
    else vPortEnterCritical();
    uint32_t header=(marker & UINT32_C(0xffc00000)) | ((uintptr_t)descriptor & UINT32_C(0x003fffff));
    if (__get_IPSR()!=0) __set_BASEPRI((uint8_t)saved);
    else vPortExitCritical();
    va_list arguments;va_start(arguments,format);
    r1_structured_log_encode_format(header,format,arguments);
    va_end(arguments);
    return 0;
}

/* Stock 0x915a8 shares the mode and BASEPRI gate with the format logger,
 * then forwards its typed vararg stream to the 0x41d30 encoder. */
uint32_t r1_structured_log_typed(uint32_t marker,const char *descriptor,...)
{
    if ((r1_structured_log_mode & 4u) && !r1_structured_log_clock_available()) return 0;
    if ((r1_structured_log_mode & 1u) && r1_structured_log_export_active()) return 0;
    uint32_t saved=0;
    if (__get_IPSR()!=0) { saved=__get_BASEPRI();__set_BASEPRI(64); }
    else vPortEnterCritical();
    uint32_t header=(marker & UINT32_C(0xffc00000)) |
                    ((uintptr_t)descriptor & UINT32_C(0x003fffff));
    if (__get_IPSR()!=0) __set_BASEPRI((uint8_t)saved);
    else vPortExitCritical();
    va_list arguments;
    va_start(arguments,descriptor);
    r1_structured_log_encode_typed(header,arguments);
    va_end(arguments);
    return 0;
}
