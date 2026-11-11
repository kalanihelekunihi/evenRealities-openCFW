/* SPDX-License-Identifier: MIT
 * Decoded CASE vector layout at 0x08000000 (46 words) and reset control
 * flow at 0x08000144 / 0x080000b8 and the 0x080000c0
 * application-entry veneer. The native 0x08000270
 * initialization-record dispatcher is semantically flattened into typed
 * CRT initialization and BSS zero calls below. Handler entries are linked
 * against the separate source candidates. The image layout is
 * g2/src/case/link/g2-case.ld.
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
    for (;;) { }
}

/* These five separate self-loops ship immediately before the referenced
 * 0x0156 default handler. The locked image has no incoming direct branch or
 * Thumb-pointer word for them, but retaining their C bodies accounts for
 * the executable bytes without encoding opcodes as data. The isolated
 * 0x91FE BX LR entry is retained in the same section. */
#define CASE_RETAINED_ENTRY \
    __attribute__((noinline,used,section(".case_retained_entries")))
CASE_RETAINED_ENTRY _Noreturn void case_vector_default_014c(void) { for (;;) { } }
CASE_RETAINED_ENTRY _Noreturn void case_vector_default_014e(void) { for (;;) { } }
CASE_RETAINED_ENTRY _Noreturn void case_vector_default_0150(void) { for (;;) { } }
CASE_RETAINED_ENTRY _Noreturn void case_vector_default_0152(void) { for (;;) { } }
CASE_RETAINED_ENTRY _Noreturn void case_vector_default_0154(void) { for (;;) { } }
CASE_RETAINED_ENTRY void case_crt_noop_91fe(void) { }
#undef CASE_RETAINED_ENTRY

/* Stock 0x08006E18 (case_hook_08006e18) */
void case_vector_svc_6e18(void) { }

/* Stock 0x08006D70 (case_vector_nmi_6d70) */
_Noreturn void case_vector_nmi_6d70(void)
{
    for (;;) { }
}

/* Stock 0x08006778 (case_vector_hardfault_6778) */
_Noreturn void case_vector_hardfault_6778(void)
{
    for (;;) { }
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

/* Stock 0x080091F0 copies whole words until the byte count reaches zero. */
__attribute__((noinline,used))
void case_crt_copy_91f0(const uint32_t *source,uint32_t *destination,uint32_t bytes)
{
    while(bytes!=0u){
        *destination++=*source++;
        bytes-=4u;
    }
}

/* Stock 0x08009200 has the same decrement-to-zero contract for BSS words. */
__attribute__((noinline,used))
uint32_t case_crt_zero_9200(const uint8_t *source,uint32_t *destination,uint32_t bytes)
{
    (void)source;
    while(bytes!=0u){
        *destination++=0u;
        bytes-=4u;
    }
    return 0u;
}

/* Stock 0x080000C0 (case_boot_application_veneer_00c0) is an alias of
 * case_application_entry_a598 in application_entry_candidate.c. */
extern void case_boot_application_veneer_00c0(void);

/* Linker-placed RAM. g2/src/case/link/g2-case.ld emits this record right
 * after the 46-word vector table and asserts it is at 0x080000b8 (stock
 * keeps its CRT record table at a fixed flash address too). Reading it by
 * address keeps the composed relocatable free of linker-defined symbols.
 * All stock-layout state is addressed absolutely inside 0x20000000..0x20002c88
 * (initialised above); named .data/.bss objects live above the MSP top. */
struct case_crt_link_regions {
    const uint32_t *data_load;
    uint32_t *data_start;
    uint32_t data_bytes;
    uint32_t *bss_start;
    uint32_t bss_bytes;
};
#define CASE_CRT_LINK_REGIONS \
    ((const struct case_crt_link_regions *)(uintptr_t)0x080000b8u)

static void case_crt_init_linked_ram(void)
{
    const struct case_crt_link_regions *r=CASE_CRT_LINK_REGIONS;
    case_crt_copy_91f0(r->data_load,r->data_start,r->data_bytes);
    case_crt_zero_9200(0,r->bss_start,r->bss_bytes);
}

/* Stock 0x08000270 (case_boot_initialize). It zeroes RAM up to the initial
 * MSP top, so it must not return: it ends in the application entry. */
_Noreturn void case_crt_init_0270(void)
{
    case_crt_init_known_defaults();
    case_crt_zero_9200(0,(uint32_t *)(uintptr_t)0x200001a4u,0x2ae4u);
    case_crt_init_linked_ram();
    case_boot_application_veneer_00c0();
    __builtin_unreachable();
}

/* Stock 0x080000B8 (case_startup_entry_00b8) reloads MSP with 0x20002c88 and
 * calls 0x0270. Reset already loads MSP from vector word 0 (the same value)
 * and only the reset path enters here, so this is plain C. */
_Noreturn void case_startup_entry_00b8(void)
{
    case_crt_init_0270();
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
