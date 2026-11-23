/* SPDX-License-Identifier: MIT
 * Wave 28: stock 0x30ecf8..0x30ef12 of g2-2.2.6.10 firmware_ble_em9305.bin, previously lowered asm (nvm_operation_gap): the application init hook
 * (second entry of the hook table), the boot loop and the NVM-while-asleep operation. Each function was run against the lowered stock extent in the
 * QEMU-ARC harness (.waves/w28, run_nvmgap1/2/3.sh) with mutants; the ROM calls, `sleep` and the loop back-edge are stubbed or cut there.
 */
#include <stdint.h>
#include "em9305_ram.h"

#define RB8(a)  (*(volatile uint8_t *)(uintptr_t)(a))
#define RW32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#ifndef EM_SLEEP
#define EM_SLEEP(n) __builtin_arc_sleep((int)(n))
#endif
#ifndef EM_AGAIN
#define EM_AGAIN 1
#endif

extern void opencfw_em9305_stock_311ee0(void);
extern uint32_t opencfw_em9305_controller_rom_boot_status(uint32_t);
extern uint32_t opencfw_em9305_controller_rom_boot_ready(uint32_t);
extern void QF_init(void);
extern uint8_t QF_maxPool_ __attribute__((section(".bss.opencfw_qf_maxpool_801360")));
extern void QF_bzero(void *start, uint32_t len);
extern void opencfw_em9305_stock_3111a8(void *pool, uint32_t size, uint32_t evt_size);
extern uint32_t em9305_rom_query_103180(void);
extern void em9305_rom_set_104ce4(uint32_t);
extern void em9305_rom_ram_ranges_1030f8(uint32_t, uint32_t);
extern void em9305_rom_gate_103c00(uint32_t);
extern uint32_t em9305_rom_wait_done_1032b4(void);
extern uint32_t opencfw_em9305_sleep_rom_start(uint32_t);
extern uint32_t opencfw_em9305_controller_startup(void);
extern void opencfw_em9305_emsys_set_configuration_mode_flag_30f720(void);
extern void em9305_rom_system_reset_103f14(void);
extern void opencfw_em9305_stock_30eb0c(void);
extern void opencfw_em9305_stock_302510(void);
extern void opencfw_em9305_stock_30ef44(const void *record, uint32_t flag, uint32_t a, uint32_t b);
extern uint32_t opencfw_em9305_stock_30ec9c(void *a, void *b);
extern void opencfw_em9305_stock_30eb48(void *a, void *b, uint32_t token);
extern const uint32_t opencfw_em9305_ini_record_335820[];
extern uint32_t opencfw_em9305_vector_table[];

/*
 * Stock 0x30ecf8 (g2-2.2.6.10 firmware_ble_em9305.bin): second entry of the application hook table (after application_main_30eb8c): SPIM module
 * registration and the framework (QF) bring-up. Cold boot only: initialise the 0x80ff6c record and call QF_init. Always: clear the 0xa0-byte pool
 * arena at (uintptr_t)&em9305_ram_80f98c and QF_poolInit it (event size 8). FLAG: the stock code leaves stale register values as the ROM arguments of rom_boot_status
 * (the record address) and rom_boot_ready (the status); kept here, ROM use unknown.
 */
void opencfw_em9305_stock_30ecf8(void)
{
  opencfw_em9305_stock_311ee0();
  em9305_ram_80faec.u32_80fb08 = 0x80ffa8u;
  em9305_ram_80fb30.u32_80fb30 = 0x10c3a8u;
  RB8(0x80ffa8u + 33u) = 1u;
  uint32_t status = opencfw_em9305_controller_rom_boot_status((uintptr_t)&em9305_ram_80faec.u32_80fb08);
  if ((status & 0x300u) == 0u || opencfw_em9305_controller_rom_boot_ready(status) != 0u) {
    RW32(0x80ff6cu) = 0x4bu;
    RW32(0x80ff6cu + 4u) = 0xb4u | (1u << 11);
    RB8(0x80ff6cu + 0x16u) = 1u;
    RB8(0x80ff6cu + 24u) = 2u;
    RB8(0x80ff6cu + 32u) = 0u;
    RB8(0x80ff6cu + 33u) = 1u;
    RB8(0x80ff6cu + 34u) = 3u;
    RB8(0x80ff6cu + 25u) = 31u;
    RB8(0x80ff6cu + 31u) = 17u;
    RB8(0x80ff6cu + 27u) = 16u;
    QF_init();
  } else {
    QF_maxPool_ = 0u;
  }
  QF_bzero((void *)(uintptr_t)&em9305_ram_80f98c, 0xa0u);
  opencfw_em9305_stock_3111a8((void *)(uintptr_t)&em9305_ram_80f98c, 0xa0u, 8u);
}

/*
 * Stock 0x30ed80 (g2-2.2.6.10 firmware_ble_em9305.bin; no symbol of its own, nothing in the image refers to it): boot loop that never returns.
 * ROM 0x103180 (nonzero: ROM 0x104ce4(1)); clears bits 5..7 of 0xf00428 and sets bit 0 of 0xf004ac; points int_vector_base (aux 0x25) at the vector
 * table. A warm resume (boot status bits 8..9 set and rom_boot_ready == 0) jumps into the middle of the loop at the wake test; otherwise (uintptr_t)&em9305_ram_801104 is
 * cleared first. Each pass: NVMEntry_CopyJLITable, NVM_InitCopy(ini record, ready flag, 1, 1); on a cold boot ROM 0x1030f8(0x5080, 0x1688) (the RAM
 * ranges outside (uintptr_t)&em9305_ram_801000..(uintptr_t)&em9305_ram_806080 and (uintptr_t)&em9305_ram_80e978..0x810000, FLAG: role unknown), then 0x302510 and 0xf00410 = 0 (cold only); the callback at ((uintptr_t)&em9305_ram_80fde0 + 0x20u),
 * controller_startup, the callback at ((uintptr_t)&em9305_ram_80fde0 + 0x1cu), set_configuration_mode_flag and a system reset. If the reset returns, the loop takes the wake test:
 * if (*0xf0383c & *(uintptr_t)&em9305_ram_801104) sleep_rom_start(3), and goes round again. FLAG: the stock code leaves stale register values as the arguments of
 * rom_boot_status/rom_boot_ready; the ROM is assumed to ignore them, 0 is passed.
 */
static int boot_is_cold(uint32_t status)
{
  return (status & 0x300u) == 0u || opencfw_em9305_controller_rom_boot_ready(0u) != 0u;
}

void opencfw_em9305_stock_30ed80(void)
{
  if (em9305_rom_query_103180() != 0u) em9305_rom_set_104ce4(1u);
  RW32(0xf00428u) = RW32(0xf00428u) & ~0xc0u;
  uint32_t v = RW32(0xf004acu) | 1u;
  RW32(0xf004acu) = v;
  __builtin_arc_sr((uint32_t)(uintptr_t)opencfw_em9305_vector_table, 0x25u);
  uint32_t status = opencfw_em9305_controller_rom_boot_status(v);
  if ((status & 0x300u) != 0u && opencfw_em9305_controller_rom_boot_ready(0u) == 0u) goto wake;
  RW32((uintptr_t)&em9305_ram_801104) = 0u;
  do {
    opencfw_em9305_stock_30eb0c();
    status = opencfw_em9305_controller_rom_boot_status(0u);
    uint32_t flag = 1u;
    if ((status & 0x300u) != 0u) flag = opencfw_em9305_controller_rom_boot_ready(0u);
    opencfw_em9305_stock_30ef44(opencfw_em9305_ini_record_335820, flag, 1u, 1u);
    if (boot_is_cold(opencfw_em9305_controller_rom_boot_status(0u)))
      em9305_rom_ram_ranges_1030f8((uintptr_t)&em9305_ram_806080 - (uintptr_t)&em9305_ram_801000, 0x810000u - (uintptr_t)&em9305_ram_80e978);
    if (boot_is_cold(opencfw_em9305_controller_rom_boot_status(0u))) {
      opencfw_em9305_stock_302510();
      RW32(0xf00410u) = 0u;
    }
    void (*cb)(void) = (void (*)(void))(uintptr_t)RW32(((uintptr_t)&em9305_ram_80fde0 + 0x20u));
    if (cb) cb();
    (void)opencfw_em9305_controller_startup();
    cb = (void (*)(void))(uintptr_t)RW32(((uintptr_t)&em9305_ram_80fde0 + 0x1cu));
    if (cb) cb();
    opencfw_em9305_emsys_set_configuration_mode_flag_30f720();
    em9305_rom_system_reset_103f14();
  wake:
    {
      uint32_t wake_bits = RW32(0xf0383cu);
      uint32_t locks = RW32((uintptr_t)&em9305_ram_801104);
      if ((locks & wake_bits) != 0u) (void)opencfw_em9305_sleep_rom_start(3u);
    }
  } while (EM_AGAIN);
}

/*
 * Stock 0x30ee78 (g2-2.2.6.10 firmware_ble_em9305.bin; no symbol of its own, reached through the 0x30ef04 and 0x30ef0c entries): NVM operation
 * with the CPU asleep. Interrupts off, ROM 0x103c00(0), NVM_BeforeOperation(buf+8, buf), the byte at 0xf0041e is set to 15 if bits 2 and 3 of the
 * byte at 0xf0383b are both set, then the argument is written to 0xf02800, `sleep 0x19` and a spin until the byte at 0xf02804 is zero. The result of ROM
 * 0x1032b4 is the return value; ROM 0x103c00(1), NVM_AfterOperation(buf+8, buf, token), the saved byte at 0xf0041e is restored under the same condition
 * and the interrupt state is restored. 0x30ef04 runs it with 8, 0x30ef0c with 4 (names of the ROM calls are address-only; FLAG: the meaning of the
 * mode value written to 0xf02800 is unknown).
 */
uint32_t opencfw_em9305_stock_30ee78(uint32_t mode)
{
  uint32_t buf[0x50 / 4];
  uint32_t irq;
  irq=(uint32_t)__builtin_arc_clri(); __builtin_arc_sync();
  em9305_rom_gate_103c00(0u);
  uint32_t token = opencfw_em9305_stock_30ec9c(&buf[2], &buf[0]);
  uint8_t saved = RB8(0xf0041eu);
  if ((RB8(0xf0383bu) & 0xcu) == 0xcu) RB8(0xf0041eu) = 15u;
  RW32(0xf02800u) = mode;
  EM_SLEEP(0x19u);
  while (RB8(0xf02804u) != 0u) {}
  uint32_t result = em9305_rom_wait_done_1032b4();
  em9305_rom_gate_103c00(1u);
  (void)__builtin_arc_clri(); __builtin_arc_sync();
  opencfw_em9305_stock_30eb48(&buf[2], &buf[0], token);
  if ((RB8(0xf0383bu) & 0xcu) == 0xcu) RB8(0xf0041eu) = saved;
  __builtin_arc_seti((int)irq);
  return result;
}

uint32_t opencfw_em9305_stock_30ef04(void) { return opencfw_em9305_stock_30ee78(8u); }
uint32_t opencfw_em9305_stock_30ef0c(void) { return opencfw_em9305_stock_30ee78(4u); }
