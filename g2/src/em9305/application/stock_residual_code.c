/* SPDX-License-Identifier: MIT
 * Stock em9305 functions (g2-2.2.6.10 firmware_ble_em9305.bin) that the rest of the C reconstruction
 * did not cover: HCI vendor helpers, interrupt-controller save/restore, NVM operation guards, PML and
 * RF helpers, PAL timer callbacks, the QP hook stubs and the libgcc signed 64-bit division.
 * Wave 26 carried them as lowered stock asm; each function below was rewritten in C from that asm and
 * checked against it in QEMU-ARC (build/em-resid/: qr.py, 100-300 random tests per function, at least
 * one mutant caught per function with branches or constants; aux registers modelled in RAM because
 * QEMU-ARC lacks the IRQ/vendor aux set). The QK SWI0/SWI1 context switch stays asm in qk_port_swi.c.
 * Fix against the wave-26 lowering: the 0x302760 extent had lost its final leave_s (stock 0x3027c6), so
 * a negative quotient ran on into the next routine; the C version returns as stock does. */

#include <stdint.h>
#include "em9305_ram.h"

#define R8(a)  (*(volatile uint8_t *)(uintptr_t)(a))
#define R16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define R32(a) (*(volatile uint32_t *)(uintptr_t)(a))

/* ARC EM auxiliary registers (ARCv2 numbering). */
#define AUX_IRQ_PRIORITY 0x206u
#define AUX_JLI_BASE     0x290u
#define AUX_IRQ_SELECT   0x40bu
#define AUX_IRQ_ENABLE   0x40cu
#define AUX_VENDOR_682   0x682u /* EM9305 vendor aux register written by RF_TestModeStop; name not known */

/* Stock RAM words that hold pointers to configuration records. */
#define EM_CONFIG_PTR    ((uintptr_t)&em9305_ram_80fb48.u32_80fb64) /* +0x14 interrupt level byte, +0x18 interrupt priority table */
#define EM_IRQ_SAVE_PTR  ((uintptr_t)&em9305_ram_80fb48.u32_80fb70)
#define EM_PML_CTX_PTR   (uintptr_t)&em9305_ram_80fb8c
#define EM_RF_CFG_PTR    ((uintptr_t)&em9305_ram_80fd2c.u32_80fd44)

/* Stock 0x302508 / 0x302510: two empty handlers after the vector table (stock bytes push_s blink;
 * pop_s blink; j_s [blink]). 0x302510 is called from application_boot.c. */
void opencfw_em9305_stock_302508(void)
{
}

void opencfw_em9305_stock_302510(void)
{
}

/* Stock 0x302760 (with its helpers 0x3026a8 and 0x302844): signed 64-bit division, the libgcc __divdi3
 * linked into the stock image. Returns a / b truncated toward zero. For b == 0 stock returns
 * 0x7fffffffffffffff (its unsigned helper yields 0x7fffffff:ffffffff and no sign fix-up is applied);
 * that result is kept. The quotient magnitude comes from a plain shift-subtract loop instead of the
 * stock 16-bit-digit (divu/macdu) and bit-serial (lp) paths; both give the exact quotient. */
static uint64_t em_udiv64(uint64_t n, uint64_t d)
{
  uint64_t q = 0u, r = 0u;
  for (uint32_t i = 0u; i < 64u; i++) {
    uint32_t carry = (uint32_t)(r >> 63);
    r = (r << 1) | (n >> 63);
    n <<= 1;
    q <<= 1;
    if (carry != 0u || r >= d) {
      r -= d;
      q |= 1u;
    }
  }
  return q;
}

int64_t opencfw_em9305_stock_302760(int64_t a, int64_t b)
{
  uint64_t ua = (a < 0) ? 0u - (uint64_t)a : (uint64_t)a;
  uint64_t ub = (b < 0) ? 0u - (uint64_t)b : (uint64_t)b;
  if (ub == 0u)
    return INT64_MAX;
  uint64_t q = em_udiv64(ua, ub);
  return (int64_t)(((a < 0) != (b < 0)) ? 0u - q : q);
}

/* Stock 0x302fa8 BbBleBisTxData: build a 20-byte BIS transmit record on the stack (kind 2 with data
 * pointer and length, or all zero when the length is 0), hand it to the radio, then queue the request
 * through 0x30fcd8 when the flag byte at (uintptr_t)&em9305_ram_8015c4 is set, else through 0x30fc68. Bytes 1..3 of the
 * record are left unwritten in the kind-2 case, as in stock. */
extern uint32_t opencfw_em9305_memset(uintptr_t dst, uint32_t value, uint32_t size);
extern uint32_t opencfw_em9305_radio_record_30fc28(uintptr_t record);
extern uint32_t opencfw_em9305_radio_request_30fcd8(uintptr_t descriptor, uint32_t selector);
extern uint32_t opencfw_em9305_radio_record_request_30fc68(uintptr_t descriptor, uint32_t selector);

struct em_bis_tx_record {
  uint8_t kind;
  uint8_t pad[3];
  uint32_t data;
  uint32_t length;
  uint32_t reserved[2];
};

uint32_t opencfw_em9305_BbBleBisTxData(uintptr_t descriptor, uint32_t selector, uint32_t data, uint32_t length)
{
  struct em_bis_tx_record record;
  if (length != 0u) {
    record.reserved[1] = 0u;
    record.reserved[0] = 0u;
    record.length = length;
    record.data = data;
    record.kind = 2u;
  } else {
    (void)opencfw_em9305_memset((uintptr_t)&record, 0u, sizeof record);
  }
  (void)opencfw_em9305_radio_record_30fc28((uintptr_t)&record);
  if (R8((uintptr_t)&em9305_ram_8015c4) != 0u)
    return opencfw_em9305_radio_request_30fcd8(descriptor, selector);
  return opencfw_em9305_radio_record_request_30fc68(descriptor, selector);
}

/* Stock 0x305ab4 EMSystem_TransmitCM: configure the radio for a vendor transmit test.
 * power: signed byte; phy (a1) 2..8 and pattern (a3) 2..4 map to 1-based selectors (0 when out of
 * range); channel (a2) goes to 0x3122c0. Returns 0x0c when 0x312430 rejects the PHY, else stores the
 * applied power level and radio status in resp[5]/resp[4], adds 2 to *len and returns 0. */
extern uint32_t opencfw_em9305_radio_status_311a00(uint32_t query);
extern uint32_t opencfw_em9305_radio_mode_312290(uint32_t mode);
extern uint32_t opencfw_em9305_radio_apply_3120a0(uint32_t first, uint32_t second);
extern uint32_t opencfw_em9305_radio_finish_apply_3122c0(uint32_t selector);
extern uint32_t opencfw_em9305_stock_312430(uint32_t mode);
extern uint32_t opencfw_em9305_stock_30f1cc(uint32_t mask, uint32_t set);

uint32_t opencfw_em9305_stock_305ab4(int32_t power, uint32_t phy, uint32_t channel, uint32_t pattern,
                                     uint8_t *resp, uint8_t *len)
{
  uint32_t status = opencfw_em9305_radio_status_311a00(1u);
  uint32_t level = opencfw_em9305_radio_mode_312290((uint32_t)(int32_t)(int8_t)power);
  uint32_t sel = pattern - 2u;
  sel = (sel < 3u) ? sel + 1u : 0u;
  (void)opencfw_em9305_radio_apply_3120a0(sel, sel);
  (void)opencfw_em9305_radio_finish_apply_3122c0(channel);
  sel = phy - 2u;
  sel = (sel < 7u) ? sel + 1u : 0u;
  if (opencfw_em9305_stock_312430(sel) == 0u)
    return 0x0cu;
  (void)opencfw_em9305_stock_30f1cc(2u, 1u);
  resp[5] = (uint8_t)level;
  resp[4] = (uint8_t)status;
  *len = (uint8_t)(*len + 2u);
  return 0u;
}

/* Stock 0x306924 IRQ_Init: program the priority of interrupts 16..65 from the table the configuration
 * record points to, set 14 in the three interrupt-controller words at 0xf009ac/0xf0099c/0xf00990 and
 * enable interrupts at the configured level (bit 4 = enable). */
void opencfw_em9305_stock_306924(void)
{
  for (uint32_t i = 0u; i < 50u; i++) {
    const volatile uint8_t *priority = (const volatile uint8_t *)(uintptr_t)em9305_ram_80fb48.u32_80fb7c;
    uint32_t level = priority[i];
    __builtin_arc_sr(i + 16u, AUX_IRQ_SELECT);
    __builtin_arc_sr(level, AUX_IRQ_PRIORITY);
  }
  R32(0xf009acu) = 0x0eu;
  __builtin_arc_sync();
  R32(0xf0099cu) = 0x0eu;
  R32(0xf00990u) = 0x0eu;
  __builtin_arc_seti((int)((em9305_ram_80fb48.u8_80fb78 & 0x0fu) | 0x10u));
}

/* Stock 0x306968 IRQ_Restore: write back 17 interrupt-controller register pairs (stride 0x24 from
 * 0xf00800, words +0 and +0xc) and the priorities of interrupts 16..65 from the save area that
 * em9305_ram_80fb48.u32_80fb70 points to (layout: 17 words, 17 words, 50 priority bytes, saved status byte; typo object em9305_ram_80110c). */
void opencfw_em9305_stock_306968(void)
{
  const volatile uint32_t *save = (const volatile uint32_t *)(uintptr_t)em9305_ram_80fb48.u32_80fb70;
  for (uint32_t i = 0u; i < 17u; i++) {
    uintptr_t reg = 0xf00800u + i * 0x24u;
    R32(reg) = save[i];
    R32(reg + 0x0cu) = save[17u + i];
  }
  const volatile uint8_t *priority = (const volatile uint8_t *)(save + 34);
  for (uint32_t i = 0u; i < 50u; i++) {
    uint32_t level = priority[i];
    __builtin_arc_sr(i + 16u, AUX_IRQ_SELECT);
    __builtin_arc_sr(level, AUX_IRQ_PRIORITY);
  }
}

/* Stock 0x3069c4 IRQ_Store: the inverse of IRQ_Restore. Saves the 17 register pairs and the 50
 * priorities, then disables interrupts and stores the previous status byte at save+186; returns the
 * status that clri returned. */
uint32_t opencfw_em9305_stock_3069c4(void)
{
  volatile uint32_t *save = (volatile uint32_t *)(uintptr_t)em9305_ram_80fb48.u32_80fb70;
  for (uint32_t i = 0u; i < 17u; i++) {
    uintptr_t reg = 0xf00800u + i * 0x24u;
    save[i] = R32(reg);
    save[17u + i] = R32(reg + 0x0cu);
  }
  volatile uint8_t *priority = (volatile uint8_t *)(save + 34);
  for (uint32_t i = 0u; i < 50u; i++) {
    __builtin_arc_sr(i + 16u, AUX_IRQ_SELECT);
    priority[i] = (uint8_t)__builtin_arc_lr(AUX_IRQ_PRIORITY);
  }
  uint32_t status = (uint32_t)__builtin_arc_clri();
  __builtin_arc_sync();
  priority[50] = (uint8_t)status;
  return status;
}

/* Stock 0x30eb0c NVMEntry_CopyJLITable: copy the JLI table [0x10b7d4, 0x10b7d4) to 0x1ff000 and point
 * JLI_BASE at the copy. The stock loop relocates each entry by (source - destination) with the vendor
 * extension instruction 0x3b100343 (major 7, minor 0x10, operands r3,r3,r13); the table is empty in
 * this image (start == end), so the loop never runs and only the JLI_BASE write has an effect. */
void opencfw_em9305_stock_30eb0c(void)
{
  __builtin_arc_sr(0x1ff000u, AUX_JLI_BASE);
}

/* Stock 0x30eb48 NVM_AfterOperation: undo NVM_BeforeOperation. Restores the 18 interrupt-controller
 * words (stride 36 from 0xf0080c), the enables of interrupts 16..20 and the priority of interrupt 0x33. */
void opencfw_em9305_stock_30eb48(const uint32_t *regs, const uint8_t *enables, uint32_t priority)
{
  for (uint32_t i = 0u; i < 18u; i++)
    R32(0xf0080cu + i * 36u) = regs[i];
  for (uint32_t i = 0u; i < 5u; i++) {
    __builtin_arc_sr(i + 16u, AUX_IRQ_SELECT);
    __builtin_arc_sr(enables[i], AUX_IRQ_ENABLE);
  }
  __builtin_arc_sr(0x33u, AUX_IRQ_SELECT);
  __builtin_arc_sr(priority, AUX_IRQ_PRIORITY);
}

/* Stock 0x30ec9c NVM_BeforeOperation: save and clear the 18 interrupt-controller words (stride 36 from
 * 0xf0080c) and the enables of interrupts 16..20, set 0xf009b4 and 0xf009c0 to 1, then save and clear
 * the priority of interrupt 0x33. Returns the saved priority (byte). */
uint32_t opencfw_em9305_stock_30ec9c(uint32_t *regs, uint8_t *enables)
{
  for (uint32_t i = 0u; i < 18u; i++) {
    uintptr_t reg = 0xf0080cu + i * 36u;
    regs[i] = R32(reg);
    R32(reg) = 0u;
  }
  for (uint32_t i = 0u; i < 5u; i++) {
    __builtin_arc_sr(i + 16u, AUX_IRQ_SELECT);
    enables[i] = (uint8_t)__builtin_arc_lr(AUX_IRQ_ENABLE);
    __builtin_arc_sr(0u, AUX_IRQ_ENABLE);
  }
  R32(0xf009b4u) = 1u;
  R32(0xf009c0u) = 1u;
  __builtin_arc_sr(0x33u, AUX_IRQ_SELECT);
  uint32_t priority = (uint32_t)__builtin_arc_lr(AUX_IRQ_PRIORITY);
  __builtin_arc_sr(0x33u, AUX_IRQ_SELECT);
  __builtin_arc_sr(0u, AUX_IRQ_PRIORITY);
  return priority & 0xffu;
}

/* Stock 0x30ef14 NVM_ErasePage: erase one page. info != 0 selects the information area (pages 0..3,
 * select bit 16), otherwise main pages 0..63. Returns 3 for an out-of-range page, else the result of
 * the NVM operation 0x30ee78(2). */
extern uint32_t opencfw_em9305_stock_30ee78(uint32_t mode);

uint32_t opencfw_em9305_stock_30ef14(uint32_t info, uint32_t page)
{
  uint32_t select;
  if (info != 0u) {
    if (page >= 4u) return 3u;
    select = 1u << 16;
  } else {
    if (page >= 0x40u) return 3u;
    select = 0u;
  }
  R32(0xf02808u) = select;
  R32(0xf0280cu) = page << 11;
  return opencfw_em9305_stock_30ee78(2u);
}

/* Stock 0x30f1cc PML_AutomaticSleepModeDisable: set (set != 0) or clear the mask bits in the PML
 * context byte +39 (automatic-sleep disable flags). Returns 1 when any mask bit was set before. */
uint32_t opencfw_em9305_stock_30f1cc(uint32_t mask, uint32_t set)
{
  uint32_t before = R8(R32(EM_PML_CTX_PTR) + 39u);
  volatile uint8_t *flags = (volatile uint8_t *)(uintptr_t)(R32(EM_PML_CTX_PTR) + 39u);
  uint32_t current = *flags;
  *flags = (uint8_t)(set != 0u ? (current | mask) : (current & ~mask));
  return (mask & before) != 0u;
}

/* Stock 0x30fa08 PML_UseLfXtalClk: with interrupts off, set (on != 0) or clear bit 3 of 0xf00404
 * (low-frequency crystal select); record the choice in PML context byte +37 and pass it to the
 * callback stored at em9305_ram_805c5c.u32_805ce0 when one is registered. */
void opencfw_em9305_stock_30fa08(uint32_t on)
{
  uint32_t status = (uint32_t)__builtin_arc_clri();
  __builtin_arc_sync();
  uint32_t clock = R8(0xf00404u) & ~8u;
  if (on != 0u) clock |= 8u;
  R8(0xf00404u) = (uint8_t)clock;
  __builtin_arc_seti((int)status);
  volatile uint8_t *ctx = (volatile uint8_t *)(uintptr_t)R32(EM_PML_CTX_PTR);
  void (*callback)(uint32_t) = (void (*)(uint32_t))(uintptr_t)em9305_ram_805c5c.u32_805ce0;
  ctx[37] = (uint8_t)on;
  if (callback != 0) callback(on);
}

/* Stock 0x31114c QF_onResumeExt, 0x3111a0 QF_onStartupExt, 0x31161c QK_onIdleExt: empty QP hooks
 * (registered in the 0x335820 init record next to the internal hooks). */
void opencfw_em9305_stock_31114c(void)
{
}

void opencfw_em9305_stock_3111a0(void)
{
}

void opencfw_em9305_stock_31161c(void)
{
}

/* Stock 0x3111a8 QF_poolInit (QP/C 6.5.1 qf_dyn.c, SDK match in g2/symbols/ble_em9305.tsv). The single
 * implementation is the upstream QF_poolInit compiled in qpc-port/qf_dyn_unit.c; this name is kept for
 * the existing callers and forwards to it. */
extern void QF_poolInit(void *poolSto, uint_fast32_t poolSize, uint_fast16_t evtSize);

void opencfw_em9305_stock_3111a8(void *poolSto, uint_fast32_t poolSize, uint_fast16_t evtSize)
{
  QF_poolInit(poolSto, poolSize, evtSize);
}

/* Stock 0x3117e8 Q_onAssertExt: disable interrupts and halt the core (kflag 1) for good. */
__attribute__((noreturn)) void opencfw_em9305_stock_3117e8(void)
{
  (void)__builtin_arc_clri();
  __builtin_arc_sync();
  for (;;)
    __builtin_arc_kflag(1u);
}

/* Stock 0x311ce8 RF_Init: clear the two 16-byte radio state blocks at (uintptr_t)&em9305_ram_8019d4 and (uintptr_t)&em9305_ram_8019c4, reset the
 * RF configuration record (bytes 0..4 = 0, 0, 10, 0, 0x3a) and continue in RF_InitHw (0x311d2c). Stock
 * reaches RF_InitHw by a tail branch with r0 still holding 0x3a; RF_InitHw reads r0, so it is passed. */
extern void opencfw_em9305_stock_311d2c(uint32_t incoming);

static void em_rf_clear_state(uintptr_t block)
{
  R32(block) = 0u;
  R32(block + 4u) = 0u;
  R32(block + 8u) = 0u;
  R16(block + 12u) = 0u;
  R16(block + 14u) = 0u;
}

void opencfw_em9305_stock_311ce8(void)
{
  em_rf_clear_state((uintptr_t)&em9305_ram_8019d4);
  em_rf_clear_state((uintptr_t)&em9305_ram_8019c4);
  R8(R32(EM_RF_CFG_PTR) + 0u) = 0u;
  R8(R32(EM_RF_CFG_PTR) + 1u) = 0u;
  R8(R32(EM_RF_CFG_PTR) + 2u) = 10u;
  R8(R32(EM_RF_CFG_PTR) + 3u) = 0u;
  R8(R32(EM_RF_CFG_PTR) + 4u) = 0x3au;
  opencfw_em9305_stock_311d2c(0x3au);
}

/* Stock 0x311db8 RF_IrqConfigure: clear and mask the radio interrupt words (0xf0085c, 0xf00868,
 * 0xf0084c = all ones) and set the radio interrupt routing word 0xf00858. */
void opencfw_em9305_stock_311db8(void)
{
  R32(0xf0085cu) = UINT32_MAX;
  __builtin_arc_sync();
  R32(0xf00868u) = UINT32_MAX;
  __builtin_arc_sync();
  R32(0xf0084cu) = UINT32_MAX;
  R32(0xf00858u) = 0x2610011u;
}

/* Stock 0x311ee0 SPIM_RegisterModule: register the SPI master module descriptor at u8_80fd38. */
void opencfw_em9305_stock_311ee0(void)
{
  em9305_ram_80faec.u32_80fb0c = (uintptr_t)&em9305_ram_80fd2c.u8_80fd38;
}

/* Stock 0x311f70 RF_SetCteDeltaRxTime: store the two CTE receive timing offsets (halfwords). */
void opencfw_em9305_stock_311f70(int32_t first, int32_t second)
{
  em9305_ram_805eec.u16_805efc = (uint16_t)second;
  em9305_ram_805eec.u16_805efe = (uint16_t)first;
}

/* Stock 0x3124bc RF_TestModeStop: stop the radio test mode (control byte 0xf04400 = 4, vendor aux 0x682
 * written 4 then 8, 0xf040bc cleared), mark it stopped at (uintptr_t)&em9305_ram_805fb8 and return 1. */
uint32_t opencfw_em9305_stock_3124bc(void)
{
  R8(0xf04400u) = 4u;
  __builtin_arc_sr(4u, AUX_VENDOR_682);
  __builtin_arc_sr(8u, AUX_VENDOR_682);
  R32(0xf040b8u) = 0u;
  R8((uintptr_t)&em9305_ram_805fb8) = 1u;
  return 1u;
}

/* Stock 0x31376c SleepTimer_Init: enable the sleep timer (0xf00458 = 1). */
void opencfw_em9305_stock_31376c(void)
{
  R8(0xf00458u) = 1u;
}

/* Stock 0x315658 bsp_LinkLayerTimeEventCallback: when the radio state (0x310260) is 0 or 1, find the
 * earliest pending compare among the enabled PAL timer channels 0, 1, 3 (compare words at
 * 0xf0181c + 4*channel, scaled by the timer divisor and taken relative to the current sleep clock),
 * store that compare in *next and return 0. Returns 1 when no channel is enabled and 2 when the radio
 * is busy. The stock scale is mpywhl (low 32 bits of word * sign-extended halfword); the divisor is a
 * byte, so a plain 32-bit multiply gives the same value. */
extern uint32_t opencfw_em9305_radio_state_310260(void);
extern uint32_t opencfw_em9305_pal_timer_divisor(void);
extern uint32_t opencfw_em9305_sleep_metadata_clock(uint32_t incoming);
extern uint32_t opencfw_em9305_pal_timer_channel_enabled(uint32_t index);
extern const uint8_t opencfw_em9305_timer_channels_334448[4];

uint32_t opencfw_em9305_stock_315658(uint32_t *next)
{
  if (opencfw_em9305_radio_state_310260() > 1u)
    return 2u;
  uint32_t divisor = opencfw_em9305_pal_timer_divisor();
  uint32_t scale = divisor & 0xffu;
  uint32_t now = opencfw_em9305_sleep_metadata_clock(divisor);
  uint32_t best = 0xffu;
  uint32_t best_delta = UINT32_MAX;
  for (uint32_t i = 0u; i < 3u; i++) {
    uint32_t channel = opencfw_em9305_timer_channels_334448[i];
    if (opencfw_em9305_pal_timer_channel_enabled(channel) == 0u)
      continue;
    uint32_t delta = R32(0xf0181cu + channel * 4u) * scale - now;
    if (delta < best_delta) {
      best = channel;
      best_delta = delta;
    }
  }
  if (best == 0xffu)
    return 1u;
  *next = R32(0xf0181cu + best * 4u) * scale;
  return 0u;
}

/* Stock 0x333404 palFrcExpiryHandler: protocol-timer compare expiry for PAL channel 0, 2 or 3. Calls
 * hook 0x10, disables the channel's compare and runs the callback registered for it
 * (u32_805e6c / u32_805e70 / u32_805e74) if any. Other channels only get the hook call. */
extern uint32_t opencfw_em9305_pal_hook_three(uint32_t value);
extern uint32_t opencfw_em9305_pal_timer_channel(uint32_t index, uint32_t enable);

void opencfw_em9305_stock_333404(uint32_t channel)
{
  uintptr_t slot;
  (void)opencfw_em9305_pal_hook_three(0x10u);
  if (channel == 3u) slot = (uintptr_t)&em9305_ram_805e6c.u32_805e74;
  else if (channel == 2u) slot = (uintptr_t)&em9305_ram_805e6c.u32_805e70;
  else if (channel == 0u) slot = (uintptr_t)&em9305_ram_805e6c.u32_805e6c;
  else return;
  (void)opencfw_em9305_pal_timer_channel(channel, 0u);
  void (*callback)(void) = (void (*)(void))(uintptr_t)R32(slot);
  if (callback != 0) callback();
}

/* Stock 0x333674 scan15_4CheckParameters: a 15.4 scan command needs 4 parameter bytes, byte 0 <= 1
 * and byte 1 (channel) <= 0x50. Returns 1 when valid. */
uint32_t opencfw_em9305_stock_333674(const uint8_t *params, uint32_t length)
{
  if (length != 4u) return 0u;
  if (params[0] > 1u) return 0u;
  if (params[1] > 0x50u) return 0u;
  return 1u;
}
