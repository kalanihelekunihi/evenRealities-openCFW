/* SPDX-License-Identifier: MIT
 * Bounded source reconstruction of the main init dispatcher at 0x41B862.
 * The called platform/allocator/storage/logger services are external cuts.
 */
#include <stdint.h>

extern void opencfw_provider_41f9d8(uint32_t);
extern void opencfw_provider_41f9f8(void);
extern void opencfw_provider_41f846(uint32_t);
extern void opencfw_provider_41ac44(void);
extern void opencfw_provider_41ac5a(uint32_t);
extern void opencfw_provider_41fa50(void);
extern void opencfw_provider_41e1e8(void);
extern void opencfw_provider_41e266(uint32_t);
extern int32_t opencfw_provider_41ba80(uint32_t);
extern void opencfw_provider_415fae(const char *, uint32_t);
extern void opencfw_provider_41fd70(void);
extern void opencfw_provider_420476(void);
extern void opencfw_provider_421210(void);
extern void opencfw_provider_4176ce(uint32_t, const char *, const char *,
                                    const char *, uint32_t, const char *);

static const char main_file[]
    __attribute__((section(".rodata.main_file"), used)) =
        "D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\bootloader\\config\\main.c";
static const char mode_error[]
    __attribute__((section(".rodata.mode_error"), used)) =
        "Error switching to high performance mode. error num = %d\r\n";
static const char boot_banner[]
    __attribute__((section(".rodata.boot_banner"), used)) =
        ">>> Even Bootloader start <<<";
static const char main_function[]
    __attribute__((section(".rodata.main_function"), used)) = "main";
static const char main_module[]
    __attribute__((section(".rodata.main_module"), used)) = "main";

__attribute__((noreturn, noinline))
void opencfw_boot_main_terminal_spin(void)
{
    for (;;) {
        __asm__ volatile("b ." ::: "memory");
    }
}

void opencfw_boot_main_init(uint32_t entry_argument)
{
    (void)entry_argument;
    opencfw_provider_41f9d8(200);
    opencfw_provider_41f9f8();
    opencfw_provider_41f846(1);
    opencfw_provider_41ac44();
    opencfw_provider_41ac5a(1);
    opencfw_provider_41fa50();
    opencfw_provider_41e1e8();
    opencfw_provider_41e266(1);

    int32_t mode_status = opencfw_provider_41ba80(2);
    if (mode_status != 0)
        opencfw_provider_415fae(mode_error, (uint32_t)mode_status);

    opencfw_provider_41fd70();
    opencfw_provider_420476();
    opencfw_provider_421210();
    opencfw_provider_4176ce(4, main_module, main_file, main_function,
                            0x2e, boot_banner);

    void (*runtime_callback)(void) =
        (void (*)(void))(uintptr_t)*(volatile uint32_t *)(uintptr_t)0x200004f4u;
    runtime_callback();
    opencfw_boot_main_terminal_spin();
}
