/* Experimental register and fatal continuation helpers for Main extended log.
 * Stock outer 0x43d580 reads IPSR; stock fatal child 0x44ab24 requests reset. */
#include <stdbool.h>
#include <stdint.h>

uint32_t g2_log_exception_number(void) {
    uint32_t ipsr;
    __asm__ volatile("mrs %0, ipsr" : "=r"(ipsr));
    return ipsr;
}

bool g2_log_is_privileged(void) {
    uint32_t ipsr, control;
    __asm__ volatile("mrs %0, ipsr" : "=r"(ipsr));
    if (ipsr != 0u) return true; /* Handler mode is privileged. */
    __asm__ volatile("mrs %0, control" : "=r"(control));
    return (control & 1u) == 0u;
}

extern void g2_recovery_reset_app(void) __attribute__((noreturn));

void g2_log_fatal_idle(void) __attribute__((noreturn));
void g2_log_fatal_idle(void) {
    /* Stock 0x44ab24 AIRCR reset. Route through g2_recovery_reset_app so the
     * early-arm OTAP key is cleared before SYSRESETREQ (see self_recovery.c). */
    g2_recovery_reset_app();
}
