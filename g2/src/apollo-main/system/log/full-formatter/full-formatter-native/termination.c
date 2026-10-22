/* Stock Main 0x541b74 -> 0x585120: fatal formatter constraint path.
 * BKPT 0xab with SYS_EXIT is the decoded architectural behavior. */
/* Stock 0x585120 (IAR exit stub: semihosting SYS_EXIT 0x18, ADP_Stopped 0x20026; 0x585120..0x585134) */
__attribute__((naked,noreturn)) void g2_main_formatter_exit(void) {
    __asm__ volatile(
        "push {r7,lr}\n"
        "nop.w\n"
        "ldr r2,=0x00020026\n"
        "1: mov r1,r2\n"
        "movs r0,#0x18\n"
        "bkpt #0xab\n"
        "b 1b\n");
}
__attribute__((naked,noreturn)) void g2_main_formatter_abort(void) {
    __asm__ volatile("movs r0,#1\nb.w g2_main_formatter_exit\n");
}
