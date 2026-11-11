/* SPDX-License-Identifier: MIT
 * Wave-6 composition closure for g2-em9305.
 *
 * ROM call bindings follow resident_rom_bindings.json / sleep_rom_bindings.c:
 * absolute IROM entry points, no ROM body bytes embedded.
 *
 * HCI command tables: em9305_hci_cmd_tables.c (stock-recovered).
 * QP ctor/top: em9305_qpc_ctor.c (QP/C 6.5.1-shaped, matches myapp ABI).
 */
#include <stdint.h>
#include <stddef.h>

/* ---- resident IROM call bindings (addresses from resident_rom_bindings.json) ---- */
uint32_t opencfw_em9305_rom_allocator_capacity_1030e8(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x1030e8u)(a); }
uint32_t opencfw_em9305_rom_cipher_block_10090c(uint32_t a, uint32_t b, uint32_t c, uint32_t d)
{ return ((uint32_t (*)(uint32_t,uint32_t,uint32_t,uint32_t))(uintptr_t)0x10090cu)(a,b,c,d); }
uint32_t opencfw_em9305_rom_cipher_key_1009c0(uint32_t a, uint32_t b)
{ return ((uint32_t (*)(uint32_t,uint32_t))(uintptr_t)0x1009c0u)(a,b); }
uint32_t opencfw_em9305_rom_curve_validate_108260(uintptr_t a)
{ return ((uint32_t (*)(uintptr_t))(uintptr_t)0x108260u)(a); }
uint32_t opencfw_em9305_rom_curve_base_108178(uintptr_t a, uintptr_t b)
{ return ((uint32_t (*)(uintptr_t,uintptr_t))(uintptr_t)0x108178u)(a,b); }
uint32_t opencfw_em9305_rom_curve_multiply_1081e8(uintptr_t a, uintptr_t b, uintptr_t c)
{ return ((uint32_t (*)(uintptr_t,uintptr_t,uintptr_t))(uintptr_t)0x1081e8u)(a,b,c); }
uint32_t opencfw_em9305_rom_radio_100dd4(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x100dd4u)(a); }
uint32_t opencfw_em9305_rom_radio_100ddc(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x100ddcu)(a); }
uint32_t opencfw_em9305_rom_radio_100fc0(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x100fc0u)(a); }
uint32_t opencfw_em9305_rom_radio_101038(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x101038u)(a); }
uint32_t opencfw_em9305_rom_radio_101054(uint32_t a)
{ return ((uint32_t (*)(uint32_t))(uintptr_t)0x101054u)(a); }
/* wave 28: the sole call site is lhciVsExtDecodeCmdPkt (stock 0x332b70, `jl 0x101e48`); args are (opcode, len, arg, 0xff, 256-byte scratch). Not in resident_rom_bindings.json (no evidence file). */
uint32_t opencfw_em9305_rom_lhci_vs_ext_101e48(uint32_t a, uint32_t b, uint32_t c, uint32_t d, uint8_t *e)
{ return ((uint32_t (*)(uint32_t,uint32_t,uint32_t,uint32_t,uint8_t *))(uintptr_t)0x101e48u)(a,b,c,d,e); }
/* wave 28: ROM entry points used by the em_system command handlers (EMSG_*, EMSMM_*). Names describe the observed use; the ROM bodies are not in the repo. */
/* 0x102588: reply to an em_system command: (op, resp length, ctx, resp buffer, callback run after the reply or 0). */
uint32_t opencfw_em9305_rom_em_cmd_reply_102588(uint32_t op, uint32_t len, uint32_t ctx, uint8_t *resp, uint32_t after)
{ return ((uint32_t (*)(uint32_t,uint32_t,uint32_t,uint8_t *,uint32_t))(uintptr_t)0x102588u)(op,len,ctx,resp,after); }
/* 0x1020e8: delay, argument 1000 in every caller (milliseconds assumed). */
void opencfw_em9305_rom_delay_1020e8(uint32_t ms)
{ ((void (*)(uint32_t))(uintptr_t)0x1020e8u)(ms); }
/* 0x104b98: apply the stored UART baud setting (name inferred; its only caller is EMSG_SetUartBaudRate_Callback). */
void opencfw_em9305_rom_uart_set_baud_104b98(uint32_t value)
{ ((void (*)(uint32_t))(uintptr_t)0x104b98u)(value); }
/* 0x100ca8 / 0x100d20: ROM word-copy routines used by the em_system memory read / write commands, (dst, src, number of 32-bit words); names describe the use. */
void opencfw_em9305_rom_copy_words_100ca8(void *dst, const void *src, uint32_t nwords)
{ ((void (*)(void *, const void *, uint32_t))(uintptr_t)0x100ca8u)(dst, src, nwords); }
void opencfw_em9305_rom_copy_words_100d20(void *dst, const void *src, uint32_t nwords)
{ ((void (*)(void *, const void *, uint32_t))(uintptr_t)0x100d20u)(dst, src, nwords); }
/* 0x10a7f8: (config, 2, 8-byte output); its callers pass three arguments, so the facade takes three. */
uint32_t opencfw_em9305_rom_random_10a7f8(uintptr_t config, uint32_t count, void *out)
{ return ((uint32_t (*)(uintptr_t, uint32_t, void *))(uintptr_t)0x10a7f8u)(config, count, out); }
/* 0x1060c4: LE cipher (name inferred from EMSS_LeEncrypt/LeDecrypt): (0, key, data, out, 128, decrypt flag) -> 0 ok, 2 busy. */
uint32_t opencfw_em9305_rom_le_cipher_1060c4(uint32_t mode, const uint8_t *key, const uint8_t *data, uint8_t *out, uint32_t bits, uint32_t decrypt)
{ return ((uint32_t (*)(uint32_t, const uint8_t *, const uint8_t *, uint8_t *, uint32_t, uint32_t))(uintptr_t)0x1060c4u)(mode, key, data, out, bits, decrypt); }
/* 0x10093c: LE cipher variant of EMSS_LeEncryptKC/LeDecryptKC: (selector byte, key, 16-byte buffer zeroed by the caller and used as output, decrypt flag) -> 0 ok, 1 failure. Name inferred. */
uint32_t opencfw_em9305_rom_le_cipher_kc_10093c(uint32_t selector, const uint8_t *key, uint8_t *buffer, uint32_t decrypt)
{ return ((uint32_t (*)(uint32_t, const uint8_t *, uint8_t *, uint32_t))(uintptr_t)0x10093cu)(selector, key, buffer, decrypt); }

void em9305_rom_hci_cmd_init_101f14(void)
{ ((void (*)(void))(uintptr_t)0x101f14u)(); }
void em9305_rom_hci_cmd_table_register_10207c(const void *table, uint32_t count)
{ ((void (*)(const void *, uint32_t))(uintptr_t)0x10207cu)(table, count); }
void em9305_rom_hci_vs_handler_register_1026bc(uintptr_t handler)
{ ((void (*)(uintptr_t))(uintptr_t)0x1026bcu)(handler); }
void em9305_rom_resume_prepare_1020d4(void)
{ ((void (*)(void))(uintptr_t)0x1020d4u)(); }
void em9305_rom_system_reset_103f14(void)
{ ((void (*)(void))(uintptr_t)0x103f14u)(); }
/* wave 28: ROM entries used by the NVM boot loop (stock 0x30ed80) and the NVM-while-asleep operation (stock 0x30ee78). The names are address-only, the roles are unknown. */
uint32_t em9305_rom_query_103180(void)
{ return ((uint32_t (*)(void))(uintptr_t)0x103180u)(); }
void em9305_rom_set_104ce4(uint32_t value)
{ ((void (*)(uint32_t))(uintptr_t)0x104ce4u)(value); }
void em9305_rom_ram_ranges_1030f8(uint32_t first, uint32_t second)
{ ((void (*)(uint32_t, uint32_t))(uintptr_t)0x1030f8u)(first, second); }
void em9305_rom_gate_103c00(uint32_t value)
{ ((void (*)(uint32_t))(uintptr_t)0x103c00u)(value); }
uint32_t em9305_rom_wait_done_1032b4(void)
{ return ((uint32_t (*)(void))(uintptr_t)0x1032b4u)(); }
/* 0x103370: (bank, page number) -> 1 stops the NVM write at 0x30f014 with result 1; role unknown (FLAG), named by address only. */
uint32_t em9305_rom_page_103370(uint32_t bank, uint32_t page)
{ return ((uint32_t (*)(uint32_t, uint32_t))(uintptr_t)0x103370u)(bank, page); }
/* 0x1030dc: no-argument ROM call; NVM_InitCopy (0x30ef44) adds its result to 0x801000 as a copy limit (inferred, FLAG); role unknown, named by address only. */
uint32_t em9305_rom_1030dc(void)
{ return ((uint32_t (*)(void))(uintptr_t)0x1030dcu)(); }
/* 0x102b00: (index, value) with value 0xd from AOAD_Init (0x30299c), one call per enabled flag byte; role unknown (FLAG), named by address only. */
void em9305_rom_102b00(uint32_t index, uint32_t value)
{ ((void (*)(uint32_t, uint32_t))(uintptr_t)0x102b00u)(index, value); }

/* ---- application RAM / hooks still owned here until BSP/WSF units land ---- */
/* Pinned to the stock RAM addresses recorded in myapp.c:54/56 (0x801970, 0x80f97c).
 * Those addresses are not re-derived here: the stock code region is not plain ARC
 * code, so only the plaintext rodata could be read (wave18). */
/* Stock evidence (wave20, ARC objdump corpus em9305/objdump/open-2026-09-29, binutils 2.42):
 * 0x30ea08 mov_s r0,0x801970 ; mov_s r1,0x30ea84 ; b 0x310d18   (ctor(&ao, initial))
 * 0x30eabc..0x30eaf4: r0=ao, r2=0x80f97c (qSto), r3=4 (qLen), r4..r6=0, jl [vtbl+8]
 *   (QActive start), so the queue is 4 x 4 B = 16 B.
 * Next stock-referenced RAM after each object: 0x801994 = 0x801970+36 and
 * 0x80f98c = 0x80f97c+16, so the 36 B and 16 B sizes are bounded by stock. */
uint8_t g2_em_myapp_ao[36] __attribute__((section(".bss.opencfw_myapp_ao_801970")));
const void *g2_em_myapp_queue[4] __attribute__((section(".bss.opencfw_myapp_queue_80f97c")));
/* ROM-owned RAM cells, pinned at their stock addresses (g2-em9305.ld). The stock
 * image never writes either: 0x8012bc is only read and decremented (0x30ead6,
 * 0x3140ec) and 0x8010a4 is only read (0x30ec6c ld r12,[0x8010a4]); the package
 * has no RAM record, so the ROM initialises them. The earlier `= 16u` in .sdata
 * was never copied to RAM by any startup code. */
uint32_t g2_em_qf_next_priority __attribute__((section(".bss.opencfw_qf_next_priority_8012bc")));
void (*g2_em_app_start_callback)(uint32_t, uint32_t, uint8_t *, uint32_t)
    __attribute__((section(".bss.opencfw_app_start_callback_8010a4")));

/* Native 0x302e80: BSP_Init stores 3 to 0xf00a78, then sync. */
void BSP_Init(void)
{
    *(volatile uint32_t *)(uintptr_t)0xf00a78u = 3u;
    __builtin_arc_sync();
}

/* Native 0x3069b8: GPIO wake user callback, read by IRQHandler_GPIO (RAM 0x80190c). */
void irq_set_user_callback_3069b8(void (*callback)(uint32_t))
{
    *(volatile uint32_t *)(uintptr_t)0x80190cu = (uint32_t)(uintptr_t)callback;
}

/* Native 0x32e5a8: vendor-specific HCI extension handler registered with the ROM
 * (0x1026bc). Allocate an event of the given type, copy the payload, send it
 * (the send takes the 2-byte header address), then hand the completion callback
 * to 0x30ae44. Always returns 1. */
extern uintptr_t opencfw_em9305_ll_event_allocate(uint32_t type, uint32_t bytes); /* 0x32e454 */
extern uint32_t opencfw_em9305_ll_event_send(uintptr_t header);                    /* 0x30ae90 */
extern uint32_t opencfw_em9305_ll_event_callback_set(uintptr_t callback);          /* 0x30ae44 */
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t bytes); /* 0x332fc4 */
uint32_t lhciCmdVsExtInterfaceEM(uint32_t type, uint32_t length, const void *payload, uintptr_t callback)
{
    uintptr_t event = opencfw_em9305_ll_event_allocate(type, (uint8_t)length);

    if (event != 0u) {
        (void)opencfw_em9305_memcpy((void *)event, payload, length);
        (void)opencfw_em9305_ll_event_send(event - 2u);
    }
    (void)opencfw_em9305_ll_event_callback_set(callback);
    return 1u;
}

/* Native 0x30482c: tail call 0x310944 with the node at RAM 0x8012e4. */
extern uint32_t opencfw_em9305_pal_metadata_register(uintptr_t node); /* 0x310944 */
void application_startup_hook_30482c(void)
{
    (void)opencfw_em9305_pal_metadata_register(0x8012e4u);
}

/* Native 0x3119a8: VoltMon_DoMeasurement(0) veneer, tail call 0x313ae4 with 0. */
extern uint32_t opencfw_em9305_timer_enable(uint32_t enable); /* 0x313ae4 */
void volt_monitor_measure_zero_3119a8(void)
{
    (void)opencfw_em9305_timer_enable(0u);
}

/* wsf_os_init_only_veneer_30460c, wsf_os_register_start_304610 and
 * wsfOsRunIdleTasks: qpc-scheduler/wsf_os_ao.c. */
