/*
 * openCFW G2 EM9305 NVM bootloader, header, entry and application linker script.
 *
 * Wave 13 evidence:
 * - EM9305 datasheet v4.5.3 (EM9305-DS.pdf, sha256 83090641...) Table 5-1:
 *   FLASH 0x300000..0x37FFFF (512 kB), DRAM0..6 0x800000..0x80FFFF (64 kB).
 *   Sec 10.5 (Fig 10-8): the optional FOTA updater sits at 0x360000. The stock
 *   2.2.6.10 package has no record there (records at 0x300000, 0x300400,
 *   0x302000 FHDR, 0x302400 app), so the app may run to the end of flash.
 * - Source bootloader starts at 0x300000 and must finish before 0x302000.
 *   It is a C candidate for the functions in stock records 0 and 1, not an
 *   instruction-identical reconstruction of those records.
 * - Header and NVM entry VMA 0x302000: record 2 is a 40-byte FHDR, a 10-byte
 *   stack/branch entry, and six erased bytes. The image finalizer computes
 *   its length and CRCs after linking.
 * - App VMA 0x302400: stock package record_3 target 0x302400, 210888 B,
 *   ends 0x335bc8. NVM = 0x300000..0x380000, so overflow fails the link.
 * - RAM: the previous 0x00080000 origin was outside the EM9305 map (it is not RAM).
 *   Units address stock RAM directly (923 distinct 0x80xxxx literals, max 0x80fe1c),
 *   so address-named sections are pinned to their stock addresses:
 *   stock pointer tables 0x3357a8 = {0x802d20,0x802fe0,0x8032a0} and
 *   0x3357b4 = {0x8035dc,0x802a60,0x80389c} (read from firmware_ble_em9305.bin).
 * - FLAG: wave18 check ( stock = g2/blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin,
 *   same sha256 91a38f7f... in all 18 official packages): the plaintext rodata table at
 *   0x335874..0x335890 = {0x80faec, 0x308, 0x80fb80, 0x80fd74, 0x80ff54, 0x80fd20, 0x80fd60, 0x80fb64}
 *   points at 0x80ff54, which is inside 0x80fe20..0x810000. So the old claim that
 *   0x80fe1c is the highest stock-referenced RAM word is wrong (it came from a code-only scan).
 *   Wave20 correction: the code record IS plain ARCv2. The corpus objdump
 *   (em9305/objdump/open-2026-09-29) decodes it with 1274 enter_s/push_s blink prologues.
 *   The wave18 count came from a mis-decoding. The only SP write is 0x32e53a mov sp,r17,
 *   with r17 from the caller/ROM, so the stack top is still not recoverable from this image.
 *   Change: MyApp AO (36 B) and queue (16 B) are pinned to their stock addresses (above).
 *   2026-10-31: g2_em_qf_next_priority and g2_em_app_start_callback are ROM-owned
 *   cells, now pinned at their stock addresses 0x8012bc / 0x8010a4 (below).
 *   Wave21 gp check (corpus objdump em9305-0x302400-0x335BC8.s): all 43 [gp,..]
 *   operands (16 loads) sit at 0x334122..0x334ca4, in the rodata tail that starts with
 *   the 12-byte-record table at 0x3340bc ({0x0000fcXX opcode, 0x0030xxxx handler, fill};
 *   verified: 0x30ec48 mov_s r0,0x3340bc), followed by byte lookup tables that objdump
 *   mis-decodes as code. No instruction writes gp, so this image
 *   never uses gp-relative addressing. The highest direct refs below 0x80ff54 are the
 *   one-word hook slots 0x80fdfc..0x80fe1c (verified: 0x3117d8 mov_s r2,0x80fe1c;
 *   ld_s r2,[r2,0]; j_s [r2], no stride). So no code in this image touches
 *   0x80fe20..0x80fe28. Still UNVERIFIED: whether the ROM uses the [0x80fd74,0x80ff54)
 *   range pair (no reference to the table from this image, ROM not in the repo).
 */
ENTRY(nvm_bootloader)

MEMORY
{
  NVM   (rx)  : ORIGIN = 0x00300000, LENGTH = 0x00080000
  DRAM  (rwx) : ORIGIN = 0x00800000, LENGTH = 0x00010000
  RAMHI (rwx) : ORIGIN = 0x0080fe20, LENGTH = 0x000001e0
}

SECTIONS
{
  .nvm_bootloader 0x00300000 : {
    KEEP(*(.nvm_bootloader.entry))
    *(.nvm_bootloader.text)
    __nvm_bootloader_end = .;
  } > NVM
  ASSERT(nvm_bootloader == 0x00300000, "EM9305 NVM bootloader must start at flash origin")
  ASSERT(__nvm_bootloader_end <= 0x00302000, "EM9305 NVM bootloader overlaps app header")

  .programHeader 0x00302000 : {
    KEEP(*(.programHeader))
  } > NVM
  ASSERT(SIZEOF(.programHeader) == 40, "EM9305 firmware header must be 40 bytes")

  .nvm_entry 0x00302028 : {
    FILL(0xFFFF)
    KEEP(*(.nvm_entry))
    . += 6;
  } > NVM
  ASSERT(SIZEOF(.nvm_entry) == 16, "EM9305 entry must be 10 bytes plus erased padding")

  /* wave27: the unmodified QP/C 6.5.1 units in qpc-port/ carry functions the stock image does not link
   * (stock has no QTicker, QF_remove_, QF_stop, QK_schedLock, QHsm_isIn, ... ) and upstream QF_init / QF_run /
   * QF_bzero, which differ from the stock bodies kept in qpc-scheduler/ (see qf_act_unit.c, qk_unit.c). */
  /DISCARD/ : {
    *(.text.QTicker_* .text.QF_getQueueMin .text.QF_remove_ .text.QF_deleteRef_ .text.QF_newRef_ .text.QF_poolGetMaxBlockSize)
    *(.text.QF_getPoolMin .text.QF_stop .text.QK_schedLock .text.QK_schedUnlock .text.QHsm_isIn .text.QHsm_childState_)
    *(.text.QEQueue_post .text.QEQueue_postLIFO .text.QEQueue_get)
    *(.text.QF_bzero_upstream_unused .text.QF_init_upstream_unused .text.QF_run_upstream_unused)
    *(.rodata.QP_versionStr .rodata.vtbl.1 .rodata.tickEvt.0)
  }
  .text 0x00302400 : {
    KEEP(*(.vectors .isr_vector))
    *(.text .text.*)
    *(.rodata .rodata.*)
    . = ALIGN(4);
    /* wave26: stock code reads 0x335bc8 (end of the stock record) in NVM_InitCopy; FLAG: assumed to mean end of image */
    opencfw_em9305_image_end = .;
  } > NVM
  ASSERT(opencfw_em9305_vector_table == 0x00302400, "vector table must sit at the application base")

  .bss.stock_802a60 0x00802a60 (NOLOAD) : { KEEP(*(.bss.opencfw_scan_context_802a60)) }
  .bss.stock_802d20 0x00802d20 (NOLOAD) : { KEEP(*(.bss.opencfw_ext_init_records_802d20)) }
  .bss.stock_8035dc 0x008035dc (NOLOAD) : { KEEP(*(.bss.opencfw_scan_context_8035dc)) }
  .bss.stock_80389c 0x0080389c (NOLOAD) : { KEEP(*(.bss.opencfw_scan_context_80389c)) }
  ASSERT(ADDR(.bss.stock_802d20) == ADDR(.bss.stock_802a60) + SIZEOF(.bss.stock_802a60), "802a60 extent")
  ASSERT(ADDR(.bss.stock_8035dc) >= ADDR(.bss.stock_802d20) + SIZEOF(.bss.stock_802d20), "802d20 extent")
  /* wave19: both pin addresses occur as limm operands in stock em9305 bin @0xca2e/0xcb0e (see em9305_link_closure.c) */
  .bss.stock_801970 0x00801970 (NOLOAD) : { KEEP(*(.bss.opencfw_myapp_ao_801970)) }
  .bss.stock_80f97c 0x0080f97c (NOLOAD) : { KEEP(*(.bss.opencfw_myapp_queue_80f97c)) }
  ASSERT(SIZEOF(.bss.stock_801970) == 36 && SIZEOF(.bss.stock_80f97c) == 16, "myapp pins")

  /* 0x8010a4 / 0x8012bc are ROM-owned cells (em9305_link_closure.c). 0x8010a4 is
   * only read; ini_record e0 writes 0x00000010 into g2_em_qf_next_priority at
   * 0x8012bc at boot, after a 2-byte pad at 0x8012ba. Reserve that pad so a
   * later pin cannot land between em9305_ram_8012b8 and the 8012bc cell
   * (0x8012c0 follows immediately). Do not grow 8012b8 across 8012bc. */
  .bss.stock_8010a4 0x008010a4 (NOLOAD) : { KEEP(*(.bss.opencfw_app_start_callback_8010a4)) }
  .bss.stock_8012ba 0x008012ba (NOLOAD) : { . += 2; }
  .bss.stock_8012bc 0x008012bc (NOLOAD) : { KEEP(*(.bss.opencfw_qf_next_priority_8012bc)) }
  ASSERT(SIZEOF(.bss.stock_8010a4) == 4 && SIZEOF(.bss.stock_8012bc) == 4, "ROM cell pins")
  ASSERT(ADDR(.bss.stock_8012ba) == 0x008012ba && SIZEOF(.bss.stock_8012ba) == 2, "8012ba hole")
  ASSERT(ADDR(.bss.stock_8012ba) + SIZEOF(.bss.stock_8012ba) == ADDR(.bss.stock_8012bc), "8012ba-8012bc adjacent")
  ASSERT(ADDR(.bss.stock_8012bc) + SIZEOF(.bss.stock_8012bc) == 0x008012c0, "8012bc-8012c0 adjacent")

  /* wave27: QP/C 6.5.1 globals at their stock addresses (qpc-port/qp_unit.h; stock code and the lowered asm address them absolutely) */
  .bss.stock_80131c 0x0080131c (NOLOAD) : { KEEP(*(.bss.opencfw_qf_active_80131c)) }
  .bss.stock_801360 0x00801360 (NOLOAD) : { KEEP(*(.bss.opencfw_qf_maxpool_801360)) }
  .bss.stock_801368 0x00801368 (NOLOAD) : { KEEP(*(.bss.opencfw_qf_pool_801368)) }
  .bss.stock_801364 0x00801364 (NOLOAD) : { KEEP(*(.bss.opencfw_qf_maxpubsignal_801364)) }
  .bss.stock_801390 0x00801390 (NOLOAD) : { KEEP(*(.bss.opencfw_qf_subscrlist_801390)) }
  .bss.stock_801394 0x00801394 (NOLOAD) : { KEEP(*(.bss.opencfw_qk_attr_801394)) }
  ASSERT(SIZEOF(.bss.stock_80131c) == 68 && SIZEOF(.bss.stock_801360) == 1 && SIZEOF(.bss.stock_801368) == 40 && SIZEOF(.bss.stock_801394) == 8 && SIZEOF(.bss.stock_801364) == 4 && SIZEOF(.bss.stock_801390) == 4, "QP global sizes")

  .sdata : {
    __SDATA_BEGIN__ = .;
    _SDA_BASE_ = .;
    *(.sdata .sdata.* .sdata2.*)
    __SDATA_END__ = .;
  } > RAMHI AT > NVM

  .data : ALIGN(4) {
    __data_start = .;
    *(.data .data.*)
    . = ALIGN(4);
    __data_end = .;
  } > RAMHI AT > NVM

  .sbss (NOLOAD) : {
    *(.sbss .sbss.* .scommon)
  } > RAMHI

  .bss (NOLOAD) : ALIGN(4) {
    __bss_start = .;
    *(.bss .bss.* COMMON)
    . = ALIGN(4);
    __bss_end = .;
  } > RAMHI
  /* RAMHI is currently empty; keep future .sdata/.data/.bss from overlapping
   * the 0x80ff54 sleep_lock_update hook object (and 0x80ffa8 beyond it). */
  ASSERT(__bss_end <= 0x0080ff54, "RAMHI must not overlap 80ff54 hook object")
}

PROVIDE(__SDATA_BEGIN__ = 0x0080fe20);
PROVIDE(__SDATA_END__ = 0x0080fe20);
PROVIDE(_SDA_BASE_ = 0x0080fe20);

/* W14: -Os codegen emits libc memcpy calls for struct copies. Route them to the
   reconstructed stock forward-copy routine (stock 0x00332fc4..0x0033301c, controller_init.c
   opencfw_em9305_memcpy; C memcpy contract = non-overlapping forward copy, which it meets). */
PROVIDE(memcpy = opencfw_em9305_memcpy);

/* BEGIN em9305_ram objects (generated by build/ws-em9305-20261122/widen/widen.py; see qpc-scheduler/em9305_ram.h) */
em9305_ram_800000 = 0x00800000;
em9305_ram_80032d = 0x0080032d;
em9305_ram_801000 = 0x00801000;
em9305_ram_801040 = 0x00801040;
em9305_ram_801090 = 0x00801090;
em9305_ram_801104 = 0x00801104;
em9305_ram_80110c = 0x0080110c;
em9305_ram_8011c8 = 0x008011c8;
em9305_ram_8011f8 = 0x008011f8;
em9305_ram_801248 = 0x00801248;
em9305_ram_801250 = 0x00801250;
em9305_ram_8012a0 = 0x008012a0;
em9305_ram_8012b8 = 0x008012b8;
em9305_ram_8012c0 = 0x008012c0;
em9305_ram_801398 = 0x00801398;
em9305_ram_80139c = 0x0080139c;
em9305_ram_8013d0 = 0x008013d0;
em9305_ram_8013f0 = 0x008013f0;
em9305_ram_8014f4 = 0x008014f4;
em9305_ram_801518 = 0x00801518;
em9305_ram_801534 = 0x00801534;
em9305_ram_8015c4 = 0x008015c4;
em9305_ram_8015dc = 0x008015dc;
em9305_ram_8015e4 = 0x008015e4;
em9305_ram_801608 = 0x00801608;
em9305_ram_801618 = 0x00801618;
em9305_ram_801638 = 0x00801638;
em9305_ram_8016bc = 0x008016bc;
em9305_ram_8016c0 = 0x008016c0;
em9305_ram_8016dc = 0x008016dc;
em9305_ram_8016f8 = 0x008016f8;
em9305_ram_8017fc = 0x008017fc;
em9305_ram_801820 = 0x00801820;
em9305_ram_801848 = 0x00801848;
em9305_ram_801864 = 0x00801864;
em9305_ram_801880 = 0x00801880;
em9305_ram_8018bc = 0x008018bc;
em9305_ram_8018f4 = 0x008018f4;
em9305_ram_801904 = 0x00801904;
em9305_ram_801908 = 0x00801908;
em9305_ram_80190c = 0x0080190c;
em9305_ram_801944 = 0x00801944;
em9305_ram_80196c = 0x0080196c;
em9305_ram_801994 = 0x00801994;
em9305_ram_8019c4 = 0x008019c4;
em9305_ram_8019d4 = 0x008019d4;
em9305_ram_8019e8 = 0x008019e8;
em9305_ram_801a04 = 0x00801a04;
em9305_ram_801a14 = 0x00801a14;
em9305_ram_801a1c = 0x00801a1c;
em9305_ram_8027cc = 0x008027cc;
em9305_ram_8027d0 = 0x008027d0;
em9305_ram_8027e0 = 0x008027e0;
em9305_ram_802850 = 0x00802850;
em9305_ram_802878 = 0x00802878;
em9305_ram_8028d0 = 0x008028d0;
em9305_ram_802950 = 0x00802950;
em9305_ram_8029ac = 0x008029ac;
em9305_ram_802a24 = 0x00802a24;
em9305_ram_802a28 = 0x00802a28;
em9305_ram_802a2c = 0x00802a2c;
em9305_ram_803560 = 0x00803560;
em9305_ram_8035c0 = 0x008035c0;
em9305_ram_803b5c = 0x00803b5c;
em9305_ram_803b68 = 0x00803b68;
em9305_ram_803b8c = 0x00803b8c;
em9305_ram_803b94 = 0x00803b94;
em9305_ram_803bb8 = 0x00803bb8;
em9305_ram_803bd4 = 0x00803bd4;
em9305_ram_803c00 = 0x00803c00;
em9305_ram_803c28 = 0x00803c28;
em9305_ram_803ca8 = 0x00803ca8;
em9305_ram_803d20 = 0x00803d20;
em9305_ram_803d58 = 0x00803d58;
em9305_ram_803d70 = 0x00803d70;
em9305_ram_804ffc = 0x00804ffc;
em9305_ram_805010 = 0x00805010;
em9305_ram_80505c = 0x0080505c;
em9305_ram_8050ec = 0x008050ec;
em9305_ram_805134 = 0x00805134;
em9305_ram_805160 = 0x00805160;
em9305_ram_80517c = 0x0080517c;
em9305_ram_805194 = 0x00805194;
em9305_ram_8051b8 = 0x008051b8;
em9305_ram_80525c = 0x0080525c;
em9305_ram_80527c = 0x0080527c;
em9305_ram_8052bc = 0x008052bc;
em9305_ram_8052d4 = 0x008052d4;
em9305_ram_8052f8 = 0x008052f8;
em9305_ram_80537c = 0x0080537c;
em9305_ram_805398 = 0x00805398;
em9305_ram_8053cc = 0x008053cc;
em9305_ram_805400 = 0x00805400;
em9305_ram_805408 = 0x00805408;
em9305_ram_80542c = 0x0080542c;
em9305_ram_805688 = 0x00805688;
em9305_ram_80578c = 0x0080578c;
em9305_ram_8057a8 = 0x008057a8;
em9305_ram_80581c = 0x0080581c;
em9305_ram_805838 = 0x00805838;
em9305_ram_805870 = 0x00805870;
em9305_ram_805880 = 0x00805880;
em9305_ram_8058ac = 0x008058ac;
em9305_ram_8058c8 = 0x008058c8;
em9305_ram_8059a0 = 0x008059a0;
em9305_ram_805a6c = 0x00805a6c;
em9305_ram_805af0 = 0x00805af0;
em9305_ram_805b60 = 0x00805b60;
em9305_ram_805b80 = 0x00805b80;
em9305_ram_805ba0 = 0x00805ba0;
em9305_ram_805bbc = 0x00805bbc;
em9305_ram_805bc1 = 0x00805bc1;
em9305_ram_805be0 = 0x00805be0;
em9305_ram_805c44 = 0x00805c44;
em9305_ram_805c5c = 0x00805c5c;
em9305_ram_805d34 = 0x00805d34;
em9305_ram_805d3c = 0x00805d3c;
em9305_ram_805e40 = 0x00805e40;
em9305_ram_805e6c = 0x00805e6c;
em9305_ram_805edc = 0x00805edc;
em9305_ram_805eec = 0x00805eec;
em9305_ram_805fb8 = 0x00805fb8;
em9305_ram_805fdc = 0x00805fdc;
em9305_ram_805ff4 = 0x00805ff4;
em9305_ram_806034 = 0x00806034;
em9305_ram_806054 = 0x00806054;
em9305_ram_80605c = 0x0080605c;
em9305_ram_806080 = 0x00806080;
em9305_ram_80e978 = 0x0080e978;
em9305_ram_80f978 = 0x0080f978;
em9305_ram_80f98c = 0x0080f98c;
em9305_ram_80faec = 0x0080faec;
em9305_ram_80fb30 = 0x0080fb30;
em9305_ram_80fb48 = 0x0080fb48;
em9305_ram_80fb8c = 0x0080fb8c;
em9305_ram_80fbbf = 0x0080fbbf;
em9305_ram_80fbd8 = 0x0080fbd8;
em9305_ram_80fbe0 = 0x0080fbe0;
em9305_ram_80fc00 = 0x0080fc00;
em9305_ram_80fc60 = 0x0080fc60;
em9305_ram_80fc80 = 0x0080fc80;
em9305_ram_80fce0 = 0x0080fce0;
em9305_ram_80fd00 = 0x0080fd00;
em9305_ram_80fd20 = 0x0080fd20;
em9305_ram_80fd2c = 0x0080fd2c;
em9305_ram_80fdd4 = 0x0080fdd4;
em9305_ram_80fde0 = 0x0080fde0;
em9305_ram_80ff54 = 0x0080ff54;
/* END em9305_ram objects */

