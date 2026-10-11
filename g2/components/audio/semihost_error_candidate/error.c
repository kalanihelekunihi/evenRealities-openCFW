/* Authenticated ARM semihost diagnostic, stock 0x4d09b4/0x541b74. */
#include <stdint.h>
static uint32_t semihost_call(uint32_t operation,uint32_t selector,
                              const void *arguments) {
    register uint32_t r0 __asm__("r0")=operation;
    register uint32_t r1 __asm__("r1")=selector;
    register const void *r2 __asm__("r2")=arguments;
    __asm__ volatile("bkpt #0xab" : "+r"(r0) : "r"(r1),"r"(r2) : "memory");
    return r0;
}
static void fatal_semihost_exit(void) __attribute__((noreturn));
static void fatal_semihost_exit(void) {
    /* Stock 0x585120 repeats SYS_EXIT(0x20026) indefinitely. */
    for(;;) (void)semihost_call(24u,0x20026u,0);
}
void g2_file_close_error(const char *message,const char *file,
                         uint32_t line) {
    const uintptr_t arguments[3]={(uintptr_t)file,line,(uintptr_t)message};
    if(semihost_call(24u,0x21010u,arguments)==0u) fatal_semihost_exit();
}
