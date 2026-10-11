/* The bounded printf wrapper passes the stock five-word engine ABI. */
#include <stdint.h>

__attribute__((naked)) int32_t opencfw_boot_format_engine(void *put,
                                                          void *context,
                                                          const char *format,
                                                          void *cursor,
                                                          uint32_t mode)
{
    __asm__ volatile("b.w opencfw_iar_format_engine");
}
