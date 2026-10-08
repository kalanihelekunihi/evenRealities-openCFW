/* Reconstruct the real IAR abort->semihosting exit path, not a replacement trap.
 * Original abort417c28, exit41b298..41b2a8; no physical trap is executed in tests. */
__attribute__((naked,noreturn)) void opencfw_iar_exit(void){__asm__ volatile(
 "push {r7,lr}\n"
 "nop.w\n"
 "ldr r2,=0x00020026\n"
 "1: mov r1,r2\n"
 "movs r0,#0x18\n"
 "bkpt #0xab\n"
 "b 1b\n");}
__attribute__((naked,noreturn)) void opencfw_format_abort_contract(void){__asm__ volatile("movs r0,#1\nb.w opencfw_iar_exit\n");}
