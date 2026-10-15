#include <stdint.h>

/* Stock entry 0x442228 reads IPSR and returns 1 in an exception context. */
uint32_t opencfw_wsf_context_is_isr(void)
{
    uint32_t ipsr;
    __asm__ volatile("mrs %0, ipsr" : "=r"(ipsr));
    return ipsr != 0u;
}
