/* Stock 0x4733ee logger error wrapper and authenticated 0x71e990 literal.
 * Formatter 0x473036 remains a typed source body contract. */
#include <stdint.h>
#include <stdarg.h>

const char g2_log_transport_queue_failure_message[] =
    "error!!!!!!elog_async_ext_output: enqueue_log failed\n";

typedef void (*transport_emit_fn)(const char *);
static transport_emit_fn volatile *const emit_cell=
    (transport_emit_fn volatile *)(uintptr_t)0x200742f0u;
static char *const error_buffer=(char *)(uintptr_t)0x2006b930u;
extern int32_t g2_log_transport_vformat_unbounded(char *buffer,
                                                    const char *format,
                                                    va_list arguments);

int32_t g2_log_transport_queue_failure(const char *format,...) {
    transport_emit_fn emit=*emit_cell;
    if(!emit) return 0;
    va_list arguments;
    va_start(arguments,format);
    int32_t written=g2_log_transport_vformat_unbounded(error_buffer,format,
                                                        arguments);
    va_end(arguments);
    emit(error_buffer);
    return written;
}
/* The radio/logging corpus's 0x4733ee import is this exact variadic body.
 * Keep the alias in the defining TU so the ABI and live emitter cell match. */
int32_t audio_ble_hci_boot_log_4733ee(const char *,...)
    __attribute__((alias("g2_log_transport_queue_failure")));
