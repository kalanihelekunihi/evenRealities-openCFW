/* SPDX-License-Identifier: MIT
 * Decoded CASE vector layout at 0x08000000 (46 words) and reset control
 * flow at 0x08000144 / 0x080000b8 and the 0x080000c0
 * application-entry veneer. The native 0x08000270
 * initialization-record dispatcher is semantically flattened into typed
 * CRT initialization and BSS zero calls below. Handler entries are linked
 * against the separate source candidates.
 * This is a separate startup candidate, not a full linked CASE image.
 */
#include <stdint.h>

extern void case_vector_pendsv_0102(void);
extern void case_vector_systick_8420(void);
extern void case_vector_irq_6e08(void);
extern void case_vector_irq_3bc8(void);
extern void case_vector_irq_3c2c(void);
extern void case_vector_irq_3d24(void);
extern void case_vector_irq_06c4(void);
extern void case_vector_irq_84b0(void);
extern void case_vector_irq_8f98(void);
extern void case_crt_init_known_defaults(void);
extern void case_application_entry_a598(void);

/* Stock 0x08000156 (case_vector_default_0156) */
_Noreturn void case_vector_default_0156(void)
{
    __asm__ volatile("1: b 1b");
    __builtin_unreachable();
}

/* Stock 0x08006E18 (case_hook_08006e18) */
void case_vector_svc_6e18(void) { }

/* Stock 0x08006D70 (case_vector_nmi_6d70) */
_Noreturn void case_vector_nmi_6d70(void)
{
    __asm__ volatile("1: b 1b");
    __builtin_unreachable();
}

/* Stock 0x08006778 (case_vector_hardfault_6778) */
_Noreturn void case_vector_hardfault_6778(void)
{
    __asm__ volatile("1: b 1b");
    __builtin_unreachable();
}

/* Stock 0x080084AE (case_early_hook_84ae) */
__attribute__((noinline,used)) static void case_early_hook_84ae(void)
{ __asm__ volatile("" ::: "memory"); }

/* Stock 0x080002D6 (case_expand_runs) */
void case_crt_decode_02d6(const uint8_t *source,uint8_t *destination,uint32_t bytes)
{
    uint8_t *end=destination+bytes;
    while(destination<end){
        uint8_t header=*source++;
        uint32_t copy=header&15u;
        uint32_t clear=header>>4;
        if(copy==0u)copy=*source++;
        if(clear==0u)clear=*source++;
        for(uint32_t i=1u;i<copy;i++)*destination++=*source++;
        for(uint32_t i=1u;i<clear;i++)*destination++=0u;
    }
}

void case_crt_zero_9200(const uint8_t *source,uint32_t *destination,uint32_t bytes)
{
    (void)source;
    for(uint32_t i=0u;i<bytes/4u;i++)destination[i]=0u;
}

/* Stock 0x080000C0 (case_boot_application_veneer_00c0) */
__attribute__((naked,noreturn)) void case_boot_application_veneer_00c0(void)
{
    __asm__ volatile(
        "ldr r0, =case_application_entry_a598\n"
        "bx r0\n");
}

/* Stock 0x08000270 (case_boot_initialize) */
__attribute__((naked,noreturn)) void case_crt_init_0270(void)
{
    __asm__ volatile(
        "bl case_crt_init_known_defaults\n"
        "movs r0, #0\n"
        "ldr r1, =0x200001a4\n"
        "ldr r2, =0x2ae4\n"
        "bl case_crt_zero_9200\n"
        "ldr r0, =case_boot_application_veneer_00c0\n"
        "bx r0\n");
}

__attribute__((naked,noreturn)) void case_startup_entry_00b8(void)
{
    __asm__ volatile(
        "ldr r0, =0x20002c88\n"
        "mov sp, r0\n"
        "bl case_crt_init_0270\n"
        "ldr r0, =case_application_entry_a598\n"
        "bx r0\n");
}

/* Stock 0x08000144 (case_reset_entry_0144) */
_Noreturn void case_reset_entry_0144(void)
{
    case_early_hook_84ae();
    case_startup_entry_00b8();
}

typedef void (*vector_handler_t)(void);
__attribute__((section(".isr_vector"),used,aligned(4)))
const vector_handler_t case_vector_table[46] = {
    [0]=(vector_handler_t)(uintptr_t)0x20002c88u,
    [1]=case_reset_entry_0144,
    [2]=case_vector_nmi_6d70,
    [3]=case_vector_hardfault_6778,
    [11]=case_vector_svc_6e18,
    [14]=case_vector_pendsv_0102,
    [15]=case_vector_systick_8420,
    [16]=case_vector_default_0156,
    [18]=case_vector_irq_6e08,
    [19]=case_vector_default_0156,
    [20]=case_vector_default_0156,
    [21]=case_vector_irq_3bc8,
    [22]=case_vector_irq_3c2c,
    [23]=case_vector_irq_3d24,
    [24]=case_vector_default_0156,
    [25]=case_vector_default_0156,
    [26]=case_vector_default_0156,
    [27]=case_vector_default_0156,
    [28]=case_vector_irq_06c4,
    [29]=case_vector_default_0156,
    [30]=case_vector_default_0156,
    [32]=case_vector_default_0156,
    [33]=case_vector_default_0156,
    [34]=case_vector_default_0156,
    [35]=case_vector_default_0156,
    [36]=case_vector_default_0156,
    [37]=case_vector_default_0156,
    [38]=case_vector_irq_84b0,
    [39]=case_vector_default_0156,
    [40]=case_vector_default_0156,
    [41]=case_vector_default_0156,
    [42]=case_vector_default_0156,
    [43]=case_vector_irq_8f98,
    [44]=case_vector_default_0156,
    [45]=case_vector_default_0156,
};
