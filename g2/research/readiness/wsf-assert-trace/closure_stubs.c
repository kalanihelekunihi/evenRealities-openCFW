#include <stdarg.h>
#include <stdint.h>

extern void WsfTrace(const char *format, ...);
extern void WsfAssert(const char *file, uint16_t line);
extern void WsfPacketTrace(uint8_t type, uint32_t length, uint8_t *buffer);

volatile uintptr_t open_cfw_wsf_assert_trace_sink;

__attribute__((noinline))
uint32_t am_util_stdio_vsprintf(char *buffer, const char *format, va_list args)
{
    open_cfw_wsf_assert_trace_sink ^= (uintptr_t)buffer;
    open_cfw_wsf_assert_trace_sink ^= (uintptr_t)format;
    (void)args;
    return (uint32_t)open_cfw_wsf_assert_trace_sink;
}

__attribute__((noinline))
uint32_t am_util_stdio_printf(const char *format, ...)
{
    open_cfw_wsf_assert_trace_sink ^= (uintptr_t)format;
    return (uint32_t)open_cfw_wsf_assert_trace_sink;
}

__attribute__((used))
void open_cfw_wsf_assert_trace_closure_root(void)
{
    uint8_t value = 0;
    WsfTrace("%u", 0u);
    WsfAssert("closure", 1u);
    WsfPacketTrace(1u, 1u, &value);
}
