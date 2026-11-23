/* SPDX-License-Identifier: MIT
 * Stock em9305 (g2-2.2.6.10 @ VMA 0x302400) data that the rest of the C reconstruction does not emit:
 * the interrupt vector table, the 0x333e9a radio tables, small rodata tables, the lctr control-PDU
 * decode table 0x334d0c and the init record 0x335820 (with the tail table 0x3357e0 before it).
 * Wave 26 emitted these as top-level asm .word/.byte directives (.waves/gendata.py); they are now C
 * objects with the same bytes and relocations: every object carries its section and alignment, and
 * no_reorder keeps them in this order inside .rodata.opencfw_em9305_stock_data (the zero pads stand
 * for the .skip bytes of the asm version). Code and data pointers are symbolic.
 * FLAG: 0x3357e0 is typed as the two 8-word primary-timer tables that
 * radio_primary_timer_333bec already uses; 0x3342d8 is the IRQ-priority map
 * (50 bytes, stock_306924) plus the UART baud table (EMSG_SetUartBaudRate);
 * 0x333ea8 is uint16[40] (common_calibrate_311ffc); 0x333ef8 starts with the
 * 20 RF_InitHw (index,value) pairs and the 40-byte apply-nibble map, with the
 * remaining 332 bytes left as bytes (RSSI calib halfwords at +160 sit in that
 * tail; later 3-byte runs are untyped). 0x3344a4 is the two 6-byte associated-
 * channel maps. 0x33445e starts with one 6-byte state-status event; the other
 * 16 bytes and the 0x333e9a / 0x333e9c / 0x3344c5 blobs stay verbatim (no
 * in-tree walker proves a type). ini_record_335820 is the version-2
 * NVM_InitCopy table (see the record comment). */
#include <stdint.h>
#include <stddef.h>
#include "em9305_ram.h"

typedef void (*em_isr_t)(void);
typedef void (*em_handler_t)(void);

extern void QF_onResumeInternalHook(void);
extern void QK_onIdleInternalHook(void);
extern void application_main_30eb8c(void);
extern void opencfw_em9305_AOAD_Init_veneer_302a1c(void);
extern void opencfw_em9305_IRQHandler_ArcTimer0(void);
extern void opencfw_em9305_IRQHandler_ArcTimer1(void);
extern void opencfw_em9305_IRQHandler_GPIO(void);
extern void opencfw_em9305_IRQHandler_PmlClock(void);
extern void opencfw_em9305_IRQHandler_PmlSvld(void);
extern void opencfw_em9305_IRQHandler_ProtocolTimerOutCmp0(void);
extern void opencfw_em9305_IRQHandler_ProtocolTimerOutCmp2(void);
extern void opencfw_em9305_IRQHandler_ProtocolTimerOutCmp3(void);
extern void opencfw_em9305_IRQHandler_ProtocolTimerOutCmp7(void);
extern void opencfw_em9305_IRQHandler_ProtocolTimerSync(void);
extern void opencfw_em9305_IRQHandler_RadioRx(void);
extern void opencfw_em9305_IRQHandler_RadioTx(void);
extern void opencfw_em9305_IRQHandler_RcCalib(void);
extern void opencfw_em9305_IRQHandler_SWI7(void);
extern void opencfw_em9305_IRQHandler_SleepTimerFullVal(void);
extern void opencfw_em9305_IRQHandler_SleepTimerOutCmp3(void);
extern void opencfw_em9305_emsys_noop_313778(void);
extern void opencfw_em9305_emsys_noop_3137f4(void);
extern void opencfw_em9305_emsys_noop_3137f8(void);
extern void opencfw_em9305_emsys_noop_pair_30f934(void);
extern void opencfw_em9305_emsys_transport_idle_code_3335c8(void);
extern void opencfw_em9305_emsys_volt_restore_mode_update_30f6dc(void);
extern void opencfw_em9305_lctrDecodeCtrlCasePduRejectInd(void);
extern void opencfw_em9305_lctrDecodeCtrlCasePduVersionInd(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCaseDefault(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduChReportingInd(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduChStatusInd(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduChannelMapInd(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduCisInd(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduCisReq(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduCisRsp(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduCisTermInd(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduClockAccuracyReq(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduClockAccuracyRsp(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduConnParamReq(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduConnParamRsp(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduConnUpdateInd(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduCteReq(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduCteRsp(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduFeatureReq(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduFeatureRsp(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduLengthReqRsp(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduMinUsedChainInd(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduPerFeatureReq(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduPeriodicSyncInd(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduPeriodicSyncWrInd(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduPhyReq(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduPhyRsp(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduPhyUpdateInd(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduPwrChangeInd(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduPwrCtrlReq(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduPwrCtrlRsp(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduRejectExtInd(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduSubrateInd(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduSubrateReq(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduTerminateInd(void);
extern void opencfw_em9305_lctrDecodeCtrlPduCasePduUnknownRsp(void);
extern void opencfw_em9305_pal_metadata_reset(void);
extern void opencfw_em9305_stock_30251c(void);
extern void opencfw_em9305_stock_3025f8(void);
extern void opencfw_em9305_stock_30299c(void);
extern void opencfw_em9305_stock_306924(void);
extern void opencfw_em9305_stock_306968(void);
extern void opencfw_em9305_stock_3069c4(void);
extern void opencfw_em9305_stock_30ecf8(void);
extern void opencfw_em9305_stock_30f170(void);
extern void opencfw_em9305_stock_30f4b0(void);
extern void opencfw_em9305_stock_310aa8(void);
extern void opencfw_em9305_stock_310c08(void);
extern void opencfw_em9305_stock_31114c(void);
extern void opencfw_em9305_stock_3111a0(void);
extern void opencfw_em9305_stock_31161c(void);
extern void opencfw_em9305_stock_3117e8(void);
extern void opencfw_em9305_stock_311ce8(void);
extern void opencfw_em9305_stock_311d2c(void);
extern void opencfw_em9305_stock_31376c(void);
extern void opencfw_em9305_stock_3137fc(void);
extern void opencfw_em9305_stock_313880(void);
extern void opencfw_em9305_stock_315658(void);
extern void qf_on_startup_internal_hook(void);

/* Interrupt vector table (int_vector_base = NVM base 0x302400, 66 entries): entry 0 is the ROM reset
 * entry, other numeric entries are ROM handlers, 0x30f170 is the default handler. */
const em_isr_t opencfw_em9305_vector_table[66] __attribute__((section(".vectors"), aligned(1024), used, no_reorder)) = {
  (em_isr_t)0x1003d0u,                                    /*  0 */
  opencfw_em9305_stock_30f170,                            /*  1 */
  opencfw_em9305_stock_30f170,                            /*  2 */
  opencfw_em9305_stock_30f170,                            /*  3 */
  opencfw_em9305_stock_30f170,                            /*  4 */
  opencfw_em9305_stock_30f170,                            /*  5 */
  opencfw_em9305_stock_30f170,                            /*  6 */
  opencfw_em9305_stock_30f170,                            /*  7 */
  opencfw_em9305_stock_30f170,                            /*  8 */
  opencfw_em9305_stock_30f170,                            /*  9 */
  opencfw_em9305_stock_30f170,                            /* 10 */
  opencfw_em9305_stock_30f170,                            /* 11 */
  opencfw_em9305_stock_30f170,                            /* 12 */
  opencfw_em9305_stock_30f170,                            /* 13 */
  opencfw_em9305_stock_30f170,                            /* 14 */
  opencfw_em9305_stock_30f170,                            /* 15 */
  opencfw_em9305_IRQHandler_ArcTimer0,                    /* 16 */
  opencfw_em9305_IRQHandler_ArcTimer1,                    /* 17 */
  opencfw_em9305_stock_30f170,                            /* 18 */
  (em_isr_t)0x102b38u,                                    /* 19 */
  (em_isr_t)0x102becu,                                    /* 20 */
  opencfw_em9305_IRQHandler_ProtocolTimerOutCmp0,         /* 21 */
  opencfw_em9305_stock_30f170,                            /* 22 */
  opencfw_em9305_IRQHandler_ProtocolTimerOutCmp2,         /* 23 */
  opencfw_em9305_IRQHandler_ProtocolTimerOutCmp3,         /* 24 */
  opencfw_em9305_IRQHandler_ProtocolTimerOutCmp7,         /* 25 */
  opencfw_em9305_IRQHandler_ProtocolTimerOutCmp7,         /* 26 */
  opencfw_em9305_IRQHandler_ProtocolTimerOutCmp7,         /* 27 */
  opencfw_em9305_IRQHandler_ProtocolTimerOutCmp7,         /* 28 */
  opencfw_em9305_stock_30f170,                            /* 29 */
  opencfw_em9305_IRQHandler_ProtocolTimerSync,            /* 30 */
  opencfw_em9305_IRQHandler_SleepTimerOutCmp3,            /* 31 */
  opencfw_em9305_IRQHandler_SleepTimerOutCmp3,            /* 32 */
  opencfw_em9305_IRQHandler_SleepTimerOutCmp3,            /* 33 */
  opencfw_em9305_IRQHandler_SleepTimerOutCmp3,            /* 34 */
  opencfw_em9305_IRQHandler_SleepTimerFullVal,            /* 35 */
  opencfw_em9305_IRQHandler_RadioTx,                      /* 36 */
  opencfw_em9305_IRQHandler_RadioRx,                      /* 37 */
  (em_isr_t)0x102d24u,                                    /* 38 */
  (em_isr_t)0x102d00u,                                    /* 39 */
  (em_isr_t)0x102dfcu,                                    /* 40 */
  (em_isr_t)0x102dd8u,                                    /* 41 */
  opencfw_em9305_IRQHandler_GPIO,                         /* 42 */
  opencfw_em9305_stock_30f170,                            /* 43 */
  opencfw_em9305_stock_30f170,                            /* 44 */
  opencfw_em9305_stock_30f170,                            /* 45 */
  opencfw_em9305_stock_30f170,                            /* 46 */
  opencfw_em9305_IRQHandler_RcCalib,                      /* 47 */
  opencfw_em9305_stock_30f170,                            /* 48 */
  opencfw_em9305_IRQHandler_PmlSvld,                      /* 49 */
  opencfw_em9305_IRQHandler_PmlClock,                     /* 50 */
  (em_isr_t)0x102cb8u,                                    /* 51 */
  opencfw_em9305_stock_30f170,                            /* 52 */
  opencfw_em9305_stock_30f170,                            /* 53 */
  opencfw_em9305_stock_30f170,                            /* 54 */
  opencfw_em9305_stock_30f170,                            /* 55 */
  opencfw_em9305_stock_30251c,                            /* 56 */
  opencfw_em9305_stock_3025f8,                            /* 57 */
  opencfw_em9305_IRQHandler_SWI7,                         /* 58 */
  opencfw_em9305_IRQHandler_SWI7,                         /* 59 */
  opencfw_em9305_IRQHandler_SWI7,                         /* 60 */
  opencfw_em9305_IRQHandler_SWI7,                         /* 61 */
  opencfw_em9305_IRQHandler_SWI7,                         /* 62 */
  opencfw_em9305_IRQHandler_SWI7,                         /* 63 */
  opencfw_em9305_stock_30f170,                            /* 64 */
  opencfw_em9305_stock_30f170,                            /* 65 */
};

static const uint8_t opencfw_em9305_stock_data_pad_333e98[2] __attribute__((section(".rodata.opencfw_em9305_stock_data"), aligned(4), used, no_reorder)) = { 0 };

const uint8_t opencfw_em9305_radio_table_333e9a[2] __attribute__((section(".rodata.opencfw_em9305_stock_data"), aligned(1), used, no_reorder)) = {
  0xff, 0xff
};

const uint8_t opencfw_em9305_radio_table_333e9c[12] __attribute__((section(".rodata.opencfw_em9305_stock_data"), aligned(1), used, no_reorder)) = {
  0x48, 0x00, 0x73, 0xfe, 0x1c, 0xff, 0x3c, 0x00, 0x5d, 0xff, 0xc6, 0xff
};

/* common_calibrate_311ffc loads these as uint16 at +32, +64 and +72 (and the
 * field/channel-strided uint16 slots in the first 32 bytes). */
const uint16_t opencfw_em9305_radio_table_333ea8[40] __attribute__((section(".rodata.opencfw_em9305_stock_data"), aligned(1), used, no_reorder)) = {
  0x0036, 0x0037, 0x0036, 0x0036, 0x005c, 0x005d, 0x005c, 0x005c,
  0x0048, 0x0049, 0x0048, 0x0048, 0x0048, 0x0049, 0x0048, 0x0048,
  0x00f3, 0x00f0, 0x00f3, 0x00f3, 0x00f3, 0x00f0, 0x00f3, 0x00f3,
  0x00f3, 0x00f0, 0x00f3, 0x00f3, 0x00f3, 0x00f0, 0x00f3, 0x00f3,
  0x008d, 0x008b, 0x008d, 0x008d, 0x0098, 0x00c0, 0x00aa, 0x00aa
};

/* RF_InitHw walks the first 20 (index, value) pairs (ini count at 80fd50 = 0x28
 * halfwords). radio_finish_apply_3122c0 reads a nibble at +80+index (index 0..39).
 * radio_measured_level_311a40 loads uint16 entries 80 and 86 (byte +160 / +172)
 * from the untyped tail. */
struct __attribute__((packed)) opencfw_em9305_radio_table_333ef8_t {
  struct __attribute__((packed)) { uint16_t index; uint16_t value; } hw_init[20];
  uint8_t apply_nibble[40];
  uint8_t tail[332];
};
const struct opencfw_em9305_radio_table_333ef8_t opencfw_em9305_radio_table_333ef8 __attribute__((section(".rodata.opencfw_em9305_stock_data"), aligned(1), used, no_reorder)) = {
  .hw_init = {
    { 0x003c, 0x001b },
    { 0x0012, 0x2049 },
    { 0x0013, 0x8a04 },
    { 0x00a6, 0x0031 },
    { 0x00ae, 0x0001 },
    { 0x00a7, 0x0b40 },
    { 0x001b, 0x95ca },
    { 0x001c, 0x2dcc },
    { 0x0018, 0x0000 },
    { 0x0019, 0x0000 },
    { 0x001a, 0x0003 },
    { 0x003d, 0x0e20 },
    { 0x0025, 0x0689 },
    { 0x0027, 0x0f09 },
    { 0x002a, 0x0689 },
    { 0x002b, 0x078c },
    { 0x002c, 0x0f09 },
    { 0x003b, 0x7350 },
    { 0x0021, 0x0065 },
    { 0x0023, 0xc903 },
  },
  .apply_nibble = {
  0x05, 0x05, 0x05, 0x05, 0x04, 0x04, 0x04, 0x04, 0x04, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03,
  0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02,
  0x02, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01
  },
  .tail = {
  0x05, 0x04, 0x04, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x02, 0x02, 0x02, 0x02, 0x01, 0x01, 0x01,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x17, 0x02, 0xb6, 0x02, 0x38, 0x03, 0xbc, 0x03,
  0x33, 0x04, 0x9f, 0x04, 0x2c, 0x02, 0xcb, 0x02, 0x4d, 0x03, 0xd2, 0x03, 0x48, 0x04, 0xb4, 0x04,
  0x10, 0x00, 0x16, 0x00, 0x39, 0x00, 0x9b, 0x01, 0x69, 0x00, 0xbb, 0x15, 0x11, 0x00, 0x20, 0x23,
  0x10, 0x00, 0x04, 0x10, 0x39, 0x00, 0x9b, 0x01, 0x69, 0x00, 0xfb, 0x0c, 0x11, 0x00, 0x43, 0x06,
  0x10, 0x00, 0x17, 0x00, 0x39, 0x00, 0x9b, 0x21, 0x69, 0x00, 0xbb, 0x15, 0x11, 0x00, 0x20, 0x23,
  0x10, 0x00, 0x17, 0x00, 0x39, 0x00, 0x9b, 0x21, 0x69, 0x00, 0xbb, 0x15, 0x11, 0x00, 0x20, 0x23,
  0xc7, 0x00, 0x00, 0xdf, 0x00, 0x01, 0xdf, 0x00, 0x01, 0xdf, 0x00, 0x01, 0xdf, 0x00, 0x01, 0xdf,
  0x00, 0x01, 0xdf, 0x00, 0x01, 0xdf, 0x00, 0x01, 0xdf, 0x00, 0x01, 0xdf, 0x00, 0x01, 0xdf, 0x00,
  0x01, 0xdf, 0x00, 0x01, 0xdf, 0x00, 0x01, 0xdf, 0x00, 0x01, 0xdf, 0x00, 0x01, 0xdf, 0x00, 0x01,
  0xdf, 0x00, 0x01, 0xdf, 0x00, 0x01, 0xdf, 0x00, 0x01, 0xdf, 0x00, 0x01, 0xdf, 0x00, 0x01, 0xdf,
  0x00, 0x01, 0xdf, 0x00, 0x01, 0xdf, 0x00, 0x01, 0xdf, 0x00, 0x01, 0xe8, 0x00, 0x03, 0xe8, 0x00,
  0x03, 0xe8, 0x00, 0x03, 0xe8, 0x00, 0x03, 0xe8, 0x00, 0x03, 0xe8, 0x00, 0x03, 0xe8, 0x00, 0x03,
  0xe8, 0x00, 0x03, 0xe8, 0x00, 0x03, 0xf1, 0x00, 0x08, 0xf1, 0x00, 0x08, 0xf1, 0x00, 0x08, 0xf1,
  0x00, 0x08, 0xf1, 0x00, 0x08, 0xf1, 0x00, 0x08, 0xf1, 0x00, 0x08, 0xf1, 0x00, 0x08, 0xf1, 0x00,
  0x08, 0xf4, 0x00, 0x0c, 0xf4, 0x00, 0x0c, 0xf4, 0x00, 0x0c, 0xf7, 0x00, 0x11, 0xf7, 0x00, 0x11,
  0xf7, 0x00, 0x11, 0xfa, 0x00, 0x19, 0xfa, 0x00, 0x19, 0xfa, 0x00, 0x19, 0xfd, 0x00, 0x25, 0xfd,
  0x00, 0x25, 0xfd, 0x00, 0x25, 0x00, 0x01, 0x2e, 0x00, 0x01, 0x2e, 0x00, 0x01, 0x2e, 0x03, 0x04,
  0x2f, 0x03, 0x04, 0x2f, 0x03, 0x04, 0x2f, 0x04, 0x04, 0x39, 0x05, 0x05, 0x3b, 0x06, 0x07, 0x3d,
  0x08, 0x08, 0x3e, 0x08, 0x08, 0x3e, 0x0a, 0x0d, 0x3f, 0x0a, 0x0d, 0x3f
  }
};


/* stock_306924 walks irq_priority[0..49] as AUX_IRQ_PRIORITY for irqs 16..65
 * (pointer installed at u32_80fb7c). EMSG_SetUartBaudRate indexes uart_baud[0..14]. */
struct opencfw_em9305_rodata_3342d8_t {
  uint8_t irq_priority[50];
  uint8_t pad_ffff[2];
  uint32_t uart_baud[15];
};
const struct opencfw_em9305_rodata_3342d8_t opencfw_em9305_rodata_3342d8 __attribute__((section(".rodata.opencfw_em9305_stock_data"), aligned(4), used, no_reorder)) = {
  .irq_priority = {
    0x05, 0x05, 0x05, 0x05, 0x05, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x02,
    0x02, 0x02, 0x02, 0x02, 0x00, 0x00, 0x04, 0x04, 0x04, 0x04, 0x06, 0x07, 0x07, 0x07, 0x07, 0x03,
    0x06, 0x05, 0x03, 0x07, 0x07, 0x07, 0x06, 0x06, 0x09, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08,
    0x08, 0x08
  },
  .pad_ffff = { 0xff, 0xff },
  .uart_baud = {
    1200u, 2400u, 4800u, 9600u, 14400u, 19200u, 28800u, 38400u,
    57600u, 76800u, 115200u, 230400u, 460800u, 921600u, 1843200u
  }
};

static const uint8_t opencfw_em9305_stock_data_pad_33445c[2] __attribute__((section(".rodata.opencfw_em9305_stock_data"), aligned(4), used, no_reorder)) = { 0 };

/* 0x33445e: state-status event (init_state_status_33445e), then the 8-byte
 * prepare template at 0x334464 (controller_init copies), then stream headers
 * at 0x33446c / 0x334470 (init_native_child_32874c / _3287b8 memcpy 4).
 * Reconstructed callers still use TU-local copies with these same bytes. */
struct __attribute__((packed)) opencfw_em9305_rodata_33445e_t {
  uint16_t handle;
  uint8_t event, status;
  uint16_t value;
  uint8_t prepare_template_334464[8];
  uint8_t stream_header_33446c[4];
  uint8_t stream_header_334470[4];
};
const struct opencfw_em9305_rodata_33445e_t opencfw_em9305_rodata_33445e __attribute__((section(".rodata.opencfw_em9305_stock_data"), aligned(1), used, no_reorder)) = {
  .handle = 0u, .event = 8u, .status = 0u, .value = 0u,
  .prepare_template_334464 = { 2u, 0u, 0u, 0u, 8u, 40u, 128u, 0u },
  .stream_header_33446c = { 0x03u, 0x00u, 0x00u, 0x08u },
  .stream_header_334470 = { 0x03u, 0x00u, 0x00u, 0x04u }
};

/* associated_channel_state_327aac: event kind[6] at 0x3344a4 and action[6] at 0x3344aa. */
struct opencfw_em9305_rodata_3344a4_t {
  uint8_t kind[6];
  uint8_t action[6];
};
const struct opencfw_em9305_rodata_3344a4_t opencfw_em9305_rodata_3344a4 __attribute__((section(".rodata.opencfw_em9305_stock_data"), aligned(4), used, no_reorder)) = {
  .kind = { 0, 0, 1, 1, 2, 2 },
  .action = { 0, 1, 0, 1, 0, 1 }
};

static const uint8_t opencfw_em9305_stock_data_pad_3344c4[1] __attribute__((section(".rodata.opencfw_em9305_stock_data"), aligned(4), used, no_reorder)) = { 0 };

const uint8_t opencfw_em9305_rodata_3344c5[3] __attribute__((section(".rodata.opencfw_em9305_stock_data"), aligned(1), used, no_reorder)) = {
  0xff, 0xff, 0xff
};

const em_handler_t opencfw_em9305_lctr_decode_actions_334d0c[43] __attribute__((section(".rodata.opencfw_em9305_stock_data"), aligned(4), used, no_reorder)) = {
  opencfw_em9305_lctrDecodeCtrlPduCasePduConnUpdateInd,
  opencfw_em9305_lctrDecodeCtrlPduCasePduChannelMapInd,
  opencfw_em9305_lctrDecodeCtrlPduCasePduTerminateInd,
  opencfw_em9305_lctrDecodeCtrlPduCaseDefault,
  opencfw_em9305_lctrDecodeCtrlPduCaseDefault,
  opencfw_em9305_lctrDecodeCtrlPduCaseDefault,
  opencfw_em9305_lctrDecodeCtrlPduCaseDefault,
  opencfw_em9305_lctrDecodeCtrlPduCasePduUnknownRsp,
  opencfw_em9305_lctrDecodeCtrlPduCasePduFeatureReq,
  opencfw_em9305_lctrDecodeCtrlPduCasePduFeatureRsp,
  opencfw_em9305_lctrDecodeCtrlPduCaseDefault,
  opencfw_em9305_lctrDecodeCtrlPduCaseDefault,
  opencfw_em9305_lctrDecodeCtrlCasePduVersionInd,
  opencfw_em9305_lctrDecodeCtrlCasePduRejectInd,
  opencfw_em9305_lctrDecodeCtrlPduCasePduPerFeatureReq,
  opencfw_em9305_lctrDecodeCtrlPduCasePduConnParamReq,
  opencfw_em9305_lctrDecodeCtrlPduCasePduConnParamRsp,
  opencfw_em9305_lctrDecodeCtrlPduCasePduRejectExtInd,
  opencfw_em9305_lctrDecodeCtrlPduCaseDefault,
  opencfw_em9305_lctrDecodeCtrlPduCaseDefault,
  opencfw_em9305_lctrDecodeCtrlPduCasePduLengthReqRsp,
  opencfw_em9305_lctrDecodeCtrlPduCasePduLengthReqRsp,
  opencfw_em9305_lctrDecodeCtrlPduCasePduPhyReq,
  opencfw_em9305_lctrDecodeCtrlPduCasePduPhyRsp,
  opencfw_em9305_lctrDecodeCtrlPduCasePduPhyUpdateInd,
  opencfw_em9305_lctrDecodeCtrlPduCasePduMinUsedChainInd,
  opencfw_em9305_lctrDecodeCtrlPduCasePduCteReq,
  opencfw_em9305_lctrDecodeCtrlPduCasePduCteRsp,
  opencfw_em9305_lctrDecodeCtrlPduCasePduPeriodicSyncInd,
  opencfw_em9305_lctrDecodeCtrlPduCasePduClockAccuracyReq,
  opencfw_em9305_lctrDecodeCtrlPduCasePduClockAccuracyRsp,
  opencfw_em9305_lctrDecodeCtrlPduCasePduCisReq,
  opencfw_em9305_lctrDecodeCtrlPduCasePduCisRsp,
  opencfw_em9305_lctrDecodeCtrlPduCasePduCisInd,
  opencfw_em9305_lctrDecodeCtrlPduCasePduCisTermInd,
  opencfw_em9305_lctrDecodeCtrlPduCasePduPwrCtrlReq,
  opencfw_em9305_lctrDecodeCtrlPduCasePduPwrCtrlRsp,
  opencfw_em9305_lctrDecodeCtrlPduCasePduPwrChangeInd,
  opencfw_em9305_lctrDecodeCtrlPduCasePduSubrateReq,
  opencfw_em9305_lctrDecodeCtrlPduCasePduSubrateInd,
  opencfw_em9305_lctrDecodeCtrlPduCasePduChReportingInd,
  opencfw_em9305_lctrDecodeCtrlPduCasePduChStatusInd,
  opencfw_em9305_lctrDecodeCtrlPduCasePduPeriodicSyncWrInd
};

/* radio_primary_timer_333bec: first-hit threshold table at 0x3357e0 and the
 * matching quantum table at 0x335800 (lp_count 8). The reconstructed reader
 * currently uses TU-local copies with these same values. */
struct opencfw_em9305_tail_3357e0_t {
  uint32_t thresholds[8];
  uint32_t quanta[8];
};
const struct opencfw_em9305_tail_3357e0_t opencfw_em9305_tail_3357e0 __attribute__((section(".rodata.opencfw_em9305_stock_data"), aligned(4), used, no_reorder)) = {
  .thresholds = { 2000000u, 1000000u, 500000u, 160000u, 80000u, 40000u, 5000u, 0u },
  .quanta = { 1000000u, 100000u, 50000u, 10000u, 5000u, 2500u, 1250u, 625u }
};

/* The 0x335820 record is a version-2 NVM_InitCopy / stock_30ef44 copy-down table
 * (application_boot.c is the only caller: stock_30ef44(record, flag, 1, 1)).
 * Signature 'I''N''I' + version 2; entries start at +4 and use _initdatCopy.
 * Each entry is {dest, signed size} then, for a positive size, data padded to 4.
 * A zero dest and size ends the list; a negative size clears -size bytes at dest.
 *
 * Typed by destination:
 *   e0 dest = &em9305_ram_8012b8 (69 B covers the 2-byte 8012b8 object, a 6-byte
 *      hole at 0x8012ba, then em9305_ram_8012c0 through u8_8012fc).
 *   e1 dest = &em9305_ram_80faec (776 B, spans 15 typo-RAM objects through 0x80fdf4).
 *   e2 dest = &em9305_ram_80fde0.u32_80fdf4 (44 B, the remainder of that 64-byte object,
 *      including the hook slots typo-proved in the 80fde0 grow).
 *   e3 dest = &em9305_ram_8012c0.u32_801300, size -19840 (BSS clear 0x801300..0x806080).
 * Payload words are symbols or dest-object fields where users or the walker prove
 * a type; leftover typo-RAM pointer literals and table bytes are noted in the
 * field comments. The linked record must stay byte-identical to the stock walker
 * input aside from relocated code-pointer values.
 */
struct __attribute__((packed)) em_ini_record_335820_t {
  uint8_t sig[3];
  uint8_t version;
  uintptr_t e0_dest;
  int32_t e0_size;
  struct __attribute__((packed)) {
    int8_t s8_8012b8;
    int8_t s8_8012b9;
    uint8_t pad_8012ba[2];
    uint32_t qf_next_priority; /* dest g2_em_qf_next_priority at 0x8012bc */
    uint32_t u32_8012c0;
    uint32_t u32_8012c4;
    uint32_t u32_8012c8;
    uint32_t u32_8012cc;
    uint32_t u32_8012d0;
    uint8_t gap_8012d4[4];
    uint32_t u32_8012d8;
    uint8_t gap_8012dc[4];
    uint32_t u32_8012e0;
    uintptr_t p_8012e4;
    uint8_t gap_8012e8[4];
    uint16_t u16_8012ec;
    uint16_t u16_8012ee;
    uintptr_t p_8012f0;
    uint8_t gap_8012f4[4];
    uint32_t u32_8012f8;
    uint8_t u8_8012fc;
    uint8_t pad[3];
  } e0;
  uintptr_t e1_dest;
  int32_t e1_size;
  struct __attribute__((packed)) {
    /* 194 words copied to 0x80faec..0x80fdf4, spanning typo-RAM objects
     * em9305_ram_80faec (17 words) through the first 0x14 bytes of em9305_ram_80fde0.
     * Code pointers are symbols. The twelve typo-RAM pointer values that
     * sleep_lock_update / IRQ_Store / PML / ProtTimer / System_Save / RF /
     * timer_context prove as object bases are named fields (or new objects).
     * Other words are unproved data (tables, zeros, scalars) and stay literals. */
    uintptr_t w[194];
  } e1;
  uintptr_t e2_dest;
  int32_t e2_size;
  struct __attribute__((packed)) {
    uint32_t u32_80fdf4;
    uint32_t u32_80fdf8;
    uintptr_t u32_80fdfc; /* application_main_30eb8c */
    uintptr_t u32_80fe00;
    uintptr_t u32_80fe04;
    uintptr_t u32_80fe08; /* QF_onResumeInternalHook */
    uintptr_t u32_80fe0c;
    uintptr_t u32_80fe10; /* qf_on_startup_internal_hook */
    uintptr_t u32_80fe14;
    uintptr_t u32_80fe18; /* QK_onIdleInternalHook */
    uintptr_t u32_80fe1c;
  } e2;
  uintptr_t e3_dest;
  int32_t e3_size;
  uintptr_t end_dest;
  int32_t end_size;
};
_Static_assert(sizeof(struct em_ini_record_335820_t) == 936, "ini_record_335820");
_Static_assert(offsetof(struct em_ini_record_335820_t, e0_dest) == 0x4, "ini_record e0_dest");
_Static_assert(offsetof(struct em_ini_record_335820_t, e1_dest) == 0x54, "ini_record e1_dest");
_Static_assert(offsetof(struct em_ini_record_335820_t, e2_dest) == 0x364, "ini_record e2_dest");
_Static_assert(offsetof(struct em_ini_record_335820_t, e3_dest) == 0x398, "ini_record e3_dest");
_Static_assert(offsetof(struct em_ini_record_335820_t, end_dest) == 0x3a0, "ini_record end");

const struct em_ini_record_335820_t opencfw_em9305_ini_record_335820 __attribute__((section(".rodata.opencfw_em9305_stock_data"), aligned(4), used, no_reorder)) = {
  .sig = { 'I', 'N', 'I' },
  .version = 2,
  .e0_dest = (uintptr_t)&em9305_ram_8012b8,
  .e0_size = 69,
  .e0 = {
    .s8_8012b8 = 6,
    .s8_8012b9 = -57, /* proved: init_native_child_310200 reads both as signed floors */
    .pad_8012ba = { 0x00, 0x00 },
    .qf_next_priority = 0x00000010u, /* g2_em_qf_next_priority; e0 writes 0x10 at boot */
    .u32_8012c0 = 0x00000000u,
    .u32_8012c4 = 0x00000000u,
    .u32_8012c8 = 0x00000000u,
    .u32_8012cc = 0x00000000u,
    .u32_8012d0 = 0x00000001u,
    .gap_8012d4 = { 0x00, 0x00, 0x00, 0x00 },
    .u32_8012d8 = 0xffffffffu,
    .gap_8012dc = { 0x1f, 0x00, 0x00, 0x00 },
    .u32_8012e0 = 0x00000001u,
    .p_8012e4 = (uintptr_t)&opencfw_em9305_stock_315658, /* dest types 0x8012e4 as u8+gap; the record stores a relocated code pointer */
    .gap_8012e8 = { 0x00, 0x00, 0x00, 0x00 },
    .u16_8012ec = 0xfb00,
    .u16_8012ee = 0xfb00,
    .p_8012f0 = (uintptr_t)&opencfw_em9305_emsys_transport_idle_code_3335c8, /* dest types 0x8012f0 as u8+gap; the record stores a relocated code pointer */
    .gap_8012f4 = { 0x00, 0x00, 0x00, 0x00 },
    .u32_8012f8 = 0x00008a04u,
    .u8_8012fc = 0xff,
    .pad = { 0x00, 0x00, 0x00 },
  },
  .e1_dest = (uintptr_t)&em9305_ram_80faec,
  .e1_size = 776,
  .e1 = {
    .w = {
    /* +0x000 -> 0x80faec */ (uintptr_t)&em9305_ram_80fb48.u32_80fb80,
    /* +0x004 -> 0x80faf0 */ (uintptr_t)&em9305_ram_80fd2c.u32_80fd74,
    /* +0x008 -> 0x80faf4 */ (uintptr_t)&em9305_ram_80ff54,
    /* +0x00c -> 0x80faf8 */ (uintptr_t)&em9305_ram_80fd20,
    /* +0x010 -> 0x80fafc */ (uintptr_t)&em9305_ram_80fd2c.u32_80fd60,
    /* +0x014 -> 0x80fb00 */ (uintptr_t)&em9305_ram_80fb48.u32_80fb64,
    /* +0x018 -> 0x80fb04 */ 0x00000000u,
    /* +0x01c -> 0x80fb08 */ 0x00000000u,
    /* +0x020 -> 0x80fb0c */ 0x00000000u,
    /* +0x024 -> 0x80fb10 */ 0x00000000u,
    /* +0x028 -> 0x80fb14 */ 0x00000000u,
    /* +0x02c -> 0x80fb18 */ 0x00000000u,
    /* +0x030 -> 0x80fb1c */ 0x00000000u,
    /* +0x034 -> 0x80fb20 */ 0x00000000u,
    /* +0x038 -> 0x80fb24 */ 0x00000000u,
    /* +0x03c -> 0x80fb28 */ 0x00000000u,
    /* +0x040 -> 0x80fb2c */ 0x00000000u,
    /* +0x044 -> 0x80fb30 */ 0x00000000u,
    /* +0x048 -> 0x80fb34 */ (uintptr_t)&opencfw_em9305_stock_30299c,
    /* +0x04c -> 0x80fb38 */ 0x00000000u,
    /* +0x050 -> 0x80fb3c */ (uintptr_t)&opencfw_em9305_AOAD_Init_veneer_302a1c,
    /* +0x054 -> 0x80fb40 */ 0x00000000u,
    /* +0x058 -> 0x80fb44 */ 0x00000000u,
    /* +0x05c -> 0x80fb48 */ 0x00000000u,
    /* +0x060 -> 0x80fb4c */ 0x00000000u,
    /* +0x064 -> 0x80fb50 */ 0x00000000u,
    /* +0x068 -> 0x80fb54 */ 0x00000000u,
    /* +0x06c -> 0x80fb58 */ 0x00000000u,
    /* +0x070 -> 0x80fb5c */ 0x00000000u,
    /* +0x074 -> 0x80fb60 */ 0x00000000u,
    /* +0x078 -> 0x80fb64 */ (uintptr_t)&opencfw_em9305_stock_306924,
    /* +0x07c -> 0x80fb68 */ (uintptr_t)&opencfw_em9305_stock_3069c4,
    /* +0x080 -> 0x80fb6c */ (uintptr_t)&opencfw_em9305_stock_306968,
    /* +0x084 -> 0x80fb70 */ (uintptr_t)&em9305_ram_80110c,
    /* +0x088 -> 0x80fb74 */ 0x00000000u,
    /* +0x08c -> 0x80fb78 */ 0x0000000au,
    /* +0x090 -> 0x80fb7c */ (uintptr_t)&opencfw_em9305_rodata_3342d8,
    /* +0x094 -> 0x80fb80 */ (uintptr_t)&opencfw_em9305_stock_30f4b0,
    /* +0x098 -> 0x80fb84 */ (uintptr_t)&opencfw_em9305_emsys_noop_pair_30f934,
    /* +0x09c -> 0x80fb88 */ (uintptr_t)&opencfw_em9305_emsys_volt_restore_mode_update_30f6dc,
    /* +0x0a0 -> 0x80fb8c */ (uintptr_t)&em9305_ram_8011c8,
    /* +0x0a4 -> 0x80fb90 */ 0x00000000u,
    /* +0x0a8 -> 0x80fb94 */ 0x0008fce6u,
    /* +0x0ac -> 0x80fb98 */ 0x000003ffu,
    /* +0x0b0 -> 0x80fb9c */ 0x000000fau,
    /* +0x0b4 -> 0x80fba0 */ 0x00000000u,
    /* +0x0b8 -> 0x80fba4 */ 0x00000030u,
    /* +0x0bc -> 0x80fba8 */ 0x00005078u,
    /* +0x0c0 -> 0x80fbac */ 0x0018ff97u,
    /* +0x0c4 -> 0x80fbb0 */ 0x00000000u,
    /* +0x0c8 -> 0x80fbb4 */ 0x0000012cu,
    /* +0x0cc -> 0x80fbb8 */ 0x00000bb8u,
    /* +0x0d0 -> 0x80fbbc */ 0x00000500u,
    /* +0x0d4 -> 0x80fbc0 */ 0x00000000u,
    /* +0x0d8 -> 0x80fbc4 */ 0x00000000u,
    /* +0x0dc -> 0x80fbc8 */ 0x00000000u,
    /* +0x0e0 -> 0x80fbcc */ 0x00000000u,
    /* +0x0e4 -> 0x80fbd0 */ 0x00000000u,
    /* +0x0e8 -> 0x80fbd4 */ 0x00000000u,
    /* +0x0ec -> 0x80fbd8 */ 0x07060404u,
    /* +0x0f0 -> 0x80fbdc */ 0x04040f0bu,
    /* +0x0f4 -> 0x80fbe0 */ 0x0e0a0e0au,
    /* +0x0f8 -> 0x80fbe4 */ 0x0c080d09u,
    /* +0x0fc -> 0x80fbe8 */ 0x0c070d08u,
    /* +0x100 -> 0x80fbec */ 0x0b060b06u,
    /* +0x104 -> 0x80fbf0 */ 0x0c060b06u,
    /* +0x108 -> 0x80fbf4 */ 0x0b050a05u,
    /* +0x10c -> 0x80fbf8 */ 0x0b050b05u,
    /* +0x110 -> 0x80fbfc */ 0x0a040904u,
    /* +0x114 -> 0x80fc00 */ 0x100a100bu,
    /* +0x118 -> 0x80fc04 */ 0x0e090e09u,
    /* +0x11c -> 0x80fc08 */ 0x0d070e08u,
    /* +0x120 -> 0x80fc0c */ 0x0d070d07u,
    /* +0x124 -> 0x80fc10 */ 0x0d060c06u,
    /* +0x128 -> 0x80fc14 */ 0x0b050d06u,
    /* +0x12c -> 0x80fc18 */ 0x0c050c05u,
    /* +0x130 -> 0x80fc1c */ 0x0c050c05u,
    /* +0x134 -> 0x80fc20 */ 0x110b120cu,
    /* +0x138 -> 0x80fc24 */ 0x100a110bu,
    /* +0x13c -> 0x80fc28 */ 0x10091009u,
    /* +0x140 -> 0x80fc2c */ 0x0f080f08u,
    /* +0x144 -> 0x80fc30 */ 0x0d070d07u,
    /* +0x148 -> 0x80fc34 */ 0x0d060c06u,
    /* +0x14c -> 0x80fc38 */ 0x0d060d06u,
    /* +0x150 -> 0x80fc3c */ 0x0c050d06u,
    /* +0x154 -> 0x80fc40 */ 0x120d120du,
    /* +0x158 -> 0x80fc44 */ 0x120d120du,
    /* +0x15c -> 0x80fc48 */ 0x120d120du,
    /* +0x160 -> 0x80fc4c */ 0x110c110cu,
    /* +0x164 -> 0x80fc50 */ 0x110a110bu,
    /* +0x168 -> 0x80fc54 */ 0x110a110au,
    /* +0x16c -> 0x80fc58 */ 0x0e080f09u,
    /* +0x170 -> 0x80fc5c */ 0x0d070e08u,
    /* +0x174 -> 0x80fc60 */ 0x0c090c09u,
    /* +0x178 -> 0x80fc64 */ 0x0b080c08u,
    /* +0x17c -> 0x80fc68 */ 0x0b070c07u,
    /* +0x180 -> 0x80fc6c */ 0x0c060b06u,
    /* +0x184 -> 0x80fc70 */ 0x0b050a06u,
    /* +0x188 -> 0x80fc74 */ 0x0b050b05u,
    /* +0x18c -> 0x80fc78 */ 0x0a040a05u,
    /* +0x190 -> 0x80fc7c */ 0x0b040a04u,
    /* +0x194 -> 0x80fc80 */ 0x0a070a07u,
    /* +0x198 -> 0x80fc84 */ 0x0a060b07u,
    /* +0x19c -> 0x80fc88 */ 0x09050a06u,
    /* +0x1a0 -> 0x80fc8c */ 0x0a050a05u,
    /* +0x1a4 -> 0x80fc90 */ 0x09040a05u,
    /* +0x1a8 -> 0x80fc94 */ 0x09040904u,
    /* +0x1ac -> 0x80fc98 */ 0x0a040a04u,
    /* +0x1b0 -> 0x80fc9c */ 0x0a040a04u,
    /* +0x1b4 -> 0x80fca0 */ 0x0b080b08u,
    /* +0x1b8 -> 0x80fca4 */ 0x0b070b08u,
    /* +0x1bc -> 0x80fca8 */ 0x0a060b07u,
    /* +0x1c0 -> 0x80fcac */ 0x0b050a06u,
    /* +0x1c4 -> 0x80fcb0 */ 0x0a050a05u,
    /* +0x1c8 -> 0x80fcb4 */ 0x09040a05u,
    /* +0x1cc -> 0x80fcb8 */ 0x09040904u,
    /* +0x1d0 -> 0x80fcbc */ 0x0a040904u,
    /* +0x1d4 -> 0x80fcc0 */ 0x12111211u,
    /* +0x1d8 -> 0x80fcc4 */ 0x0e0c100eu,
    /* +0x1dc -> 0x80fcc8 */ 0x0c0a0d0bu,
    /* +0x1e0 -> 0x80fccc */ 0x0b080c09u,
    /* +0x1e4 -> 0x80fcd0 */ 0x0a070b08u,
    /* +0x1e8 -> 0x80fcd4 */ 0x09060a07u,
    /* +0x1ec -> 0x80fcd8 */ 0x0a060906u,
    /* +0x1f0 -> 0x80fcdc */ 0x09050a06u,
    /* +0x1f4 -> 0x80fce0 */ 0x08040804u,
    /* +0x1f8 -> 0x80fce4 */ 0x08040804u,
    /* +0x1fc -> 0x80fce8 */ 0x0a040804u,
    /* +0x200 -> 0x80fcec */ 0x0b040a04u,
    /* +0x204 -> 0x80fcf0 */ 0x0e040b04u,
    /* +0x208 -> 0x80fcf4 */ 0x11040e04u,
    /* +0x20c -> 0x80fcf8 */ 0x16041104u,
    /* +0x210 -> 0x80fcfc */ 0x16041604u,
    /* +0x214 -> 0x80fd00 */ 0x09040904u,
    /* +0x218 -> 0x80fd04 */ 0x09040904u,
    /* +0x21c -> 0x80fd08 */ 0x0b040904u,
    /* +0x220 -> 0x80fd0c */ 0x0d040b04u,
    /* +0x224 -> 0x80fd10 */ 0x11040d04u,
    /* +0x228 -> 0x80fd14 */ 0x16041104u,
    /* +0x22c -> 0x80fd18 */ 0x16041604u,
    /* +0x230 -> 0x80fd1c */ 0x16041604u,
    /* +0x234 -> 0x80fd20 */ (uintptr_t)&opencfw_em9305_pal_metadata_reset,
    /* +0x238 -> 0x80fd24 */ (uintptr_t)&opencfw_em9305_stock_310c08,
    /* +0x23c -> 0x80fd28 */ (uintptr_t)&opencfw_em9305_stock_310aa8,
    /* +0x240 -> 0x80fd2c */ (uintptr_t)&em9305_ram_8011f8,
    /* +0x244 -> 0x80fd30 */ 0x00000000u,
    /* +0x248 -> 0x80fd34 */ 0x07d00000u,
    /* +0x24c -> 0x80fd38 */ (uintptr_t)&opencfw_em9305_stock_311ce8,
    /* +0x250 -> 0x80fd3c */ 0x00000000u,
    /* +0x254 -> 0x80fd40 */ (uintptr_t)&opencfw_em9305_stock_311d2c,
    /* +0x258 -> 0x80fd44 */ (uintptr_t)&em9305_ram_801248,
    /* +0x25c -> 0x80fd48 */ 0x00000000u,
    /* +0x260 -> 0x80fd4c */ (uintptr_t)&opencfw_em9305_radio_table_333ef8,
    /* +0x264 -> 0x80fd50 */ 0x00000028u,
    /* +0x268 -> 0x80fd54 */ (uintptr_t)&opencfw_em9305_radio_table_333ea8,
    /* +0x26c -> 0x80fd58 */ (uintptr_t)&opencfw_em9305_radio_table_333e9c,
    /* +0x270 -> 0x80fd5c */ 0x00000810u,
    /* +0x274 -> 0x80fd60 */ (uintptr_t)&opencfw_em9305_stock_31376c,
    /* +0x278 -> 0x80fd64 */ (uintptr_t)&opencfw_em9305_emsys_noop_3137f4,
    /* +0x27c -> 0x80fd68 */ (uintptr_t)&opencfw_em9305_emsys_noop_313778,
    /* +0x280 -> 0x80fd6c */ 0x00000000u,
    /* +0x284 -> 0x80fd70 */ 0x00000000u,
    /* +0x288 -> 0x80fd74 */ (uintptr_t)&opencfw_em9305_emsys_noop_3137f8,
    /* +0x28c -> 0x80fd78 */ (uintptr_t)&opencfw_em9305_stock_313880,
    /* +0x290 -> 0x80fd7c */ (uintptr_t)&opencfw_em9305_stock_3137fc,
    /* +0x294 -> 0x80fd80 */ (uintptr_t)&em9305_ram_801250,
    /* +0x298 -> 0x80fd84 */ 0x00000000u,
    /* +0x29c -> 0x80fd88 */ 0x00000000u,
    /* +0x2a0 -> 0x80fd8c */ 0x00000000u,
    /* +0x2a4 -> 0x80fd90 */ 0x00000000u,
    /* +0x2a8 -> 0x80fd94 */ 0x00000000u,
    /* +0x2ac -> 0x80fd98 */ 0x00000000u,
    /* +0x2b0 -> 0x80fd9c */ 0x00000000u,
    /* +0x2b4 -> 0x80fda0 */ 0x00000000u,
    /* +0x2b8 -> 0x80fda4 */ 0x00000000u,
    /* +0x2bc -> 0x80fda8 */ 0x00000000u,
    /* +0x2c0 -> 0x80fdac */ 0x00000000u,
    /* +0x2c4 -> 0x80fdb0 */ 0x00000000u,
    /* +0x2c8 -> 0x80fdb4 */ 0x00000000u,
    /* +0x2cc -> 0x80fdb8 */ 0x00000000u,
    /* +0x2d0 -> 0x80fdbc */ 0x00000000u,
    /* +0x2d4 -> 0x80fdc0 */ 0x00000000u,
    /* +0x2d8 -> 0x80fdc4 */ 0x00000000u,
    /* +0x2dc -> 0x80fdc8 */ 0x00000000u,
    /* +0x2e0 -> 0x80fdcc */ 0x00000000u,
    /* +0x2e4 -> 0x80fdd0 */ 0x00000000u,
    /* +0x2e8 -> 0x80fdd4 */ 0x00000000u,
    /* +0x2ec -> 0x80fdd8 */ 0x00000000u,
    /* +0x2f0 -> 0x80fddc */ 0x00000000u,
    /* +0x2f4 -> 0x80fde0 */ (uintptr_t)&em9305_ram_8012a0,
    /* +0x2f8 -> 0x80fde4 */ 0x00000000u,
    /* +0x2fc -> 0x80fde8 */ 0x0000a2c3u,
    /* +0x300 -> 0x80fdec */ 0x00c80190u,
    /* +0x304 -> 0x80fdf0 */ 0x00000000u,
    },
  },
  .e2_dest = (uintptr_t)&em9305_ram_80fde0.u32_80fdf4,
  .e2_size = 44,
  .e2 = {
    .u32_80fdf4 = 0x00000000u,
    .u32_80fdf8 = 0x00000000u,
    .u32_80fdfc = (uintptr_t)&application_main_30eb8c,
    .u32_80fe00 = (uintptr_t)&opencfw_em9305_stock_30ecf8,
    .u32_80fe04 = (uintptr_t)&opencfw_em9305_stock_31114c,
    .u32_80fe08 = (uintptr_t)&QF_onResumeInternalHook,
    .u32_80fe0c = (uintptr_t)&opencfw_em9305_stock_3111a0,
    .u32_80fe10 = (uintptr_t)&qf_on_startup_internal_hook,
    .u32_80fe14 = (uintptr_t)&opencfw_em9305_stock_31161c,
    .u32_80fe18 = (uintptr_t)&QK_onIdleInternalHook,
    .u32_80fe1c = (uintptr_t)&opencfw_em9305_stock_3117e8,
  },
  .e3_dest = (uintptr_t)&em9305_ram_8012c0.u32_801300,
  .e3_size = -19840,
  .end_dest = 0,
  .end_size = 0,
};


_Static_assert(sizeof(struct opencfw_em9305_radio_table_333ef8_t) == 452, "333ef8 size");
_Static_assert(sizeof(struct opencfw_em9305_rodata_3342d8_t) == 112, "3342d8 size");
_Static_assert(sizeof(struct opencfw_em9305_rodata_33445e_t) == 22, "33445e size");
_Static_assert(sizeof(struct opencfw_em9305_rodata_3344a4_t) == 12, "3344a4 size");
_Static_assert(sizeof(struct opencfw_em9305_tail_3357e0_t) == 64, "3357e0 size");
