/* SPDX-License-Identifier: MIT */
ENTRY(open_cfw_em9305_load_u8_303e50)

open_cfw_em9305_memset_33301c = 0x0033301c;

SECTIONS
{
  .tail_303e50 0x00303e50 : { KEEP(*(.text.entry.open_cfw_em9305_load_u8_303e50)) }
  .tail_303e5c 0x00303e5c : { KEEP(*(.text.entry.open_cfw_em9305_load_u8_303e5c)) }
  .tail_303f50 0x00303f50 : { KEEP(*(.text.entry.open_cfw_em9305_load_u8_303f50)) }
  .tail_303f68 0x00303f68 : { KEEP(*(.text.entry.open_cfw_em9305_load_u32_303f68)) }
  .tail_3047b0 0x003047b0 : { KEEP(*(.text.entry.open_cfw_em9305_equals_one_3047b0)) }
  .tail_3069b8 0x003069b8 : { KEEP(*(.text.entry.open_cfw_em9305_store_u32_3069b8)) }
  .tail_307c08 0x00307c08 : { KEEP(*(.text.entry.open_cfw_em9305_nonzero_307c08)) }
  .tail_307dd8 0x00307dd8 : { KEEP(*(.text.entry.open_cfw_em9305_nonzero_307dd8)) }
  .tail_30f368 0x0030f368 : { KEEP(*(.text.entry.open_cfw_em9305_load_u16_30f368)) }
  .tail_30f710 0x0030f710 : { KEEP(*(.text.entry.open_cfw_em9305_set_bit23_30f710)) }
  .tail_30f720 0x0030f720 : { KEEP(*(.text.entry.open_cfw_em9305_set_bit23_30f720)) }
  .tail_310480 0x00310480 : { KEEP(*(.text.entry.open_cfw_em9305_store_u8_310480)) }
  .tail_31048c 0x0031048c : { KEEP(*(.text.entry.open_cfw_em9305_store_u8_31048c)) }
  .tail_3108f4 0x003108f4 : { KEEP(*(.text.entry.open_cfw_em9305_load_u32_3108f4)) }
  .tail_311f84 0x00311f84 : { KEEP(*(.text.entry.open_cfw_em9305_store_u16_311f84)) }
  .tail_3122f0 0x003122f0 : { KEEP(*(.text.entry.open_cfw_em9305_store_u8_3122f0)) }
  .tail_31369c 0x0031369c : { KEEP(*(.text.entry.open_cfw_em9305_zero_144_31369c)) }
  .tail_313760 0x00313760 : { KEEP(*(.text.entry.open_cfw_em9305_load_u16_313760)) }
  .tail_31b2f8 0x0031b2f8 : { KEEP(*(.text.entry.open_cfw_em9305_load_offset23_31b2f8)) }
  .tail_32cac4 0x0032cac4 : { KEEP(*(.text.entry.open_cfw_em9305_store_40_32cac4)) }
  .tail_32cacc 0x0032cacc : { KEEP(*(.text.entry.open_cfw_em9305_store_30_32cacc)) }
  .tail_32cad4 0x0032cad4 : { KEEP(*(.text.entry.open_cfw_em9305_store_48_32cad4)) }
  .tail_32cadc 0x0032cadc : { KEEP(*(.text.entry.open_cfw_em9305_store_34_32cadc)) }

  .meta_302664 0x00302664 : { KEEP(*(.text.meta.entry.302664)) }
  .meta_302748 0x00302748 : { KEEP(*(.text.meta.entry.302748)) }
  .meta_302760 0x00302760 : { KEEP(*(.text.meta.entry.302760)) }
  .meta_3027c8 0x003027c8 : { KEEP(*(.text.meta.entry.3027c8)) }
  .meta_3027f4 0x003027f4 : { KEEP(*(.text.meta.entry.3027f4)) }
  .meta_302820 0x00302820 : { KEEP(*(.text.meta.entry.302820)) }
  .meta_332fc4 0x00332fc4 : { KEEP(*(.text.meta.entry.332fc4)) }
  .meta_33301c 0x0033301c : { KEEP(*(.text.meta.entry.33301c)) }

  .noop_302d80 0x00302d80 : { KEEP(*(.text.impl.open_cfw_em9305_noop_302d80)) }
  .noop_304eb4 0x00304eb4 : { KEEP(*(.text.impl.open_cfw_em9305_noop_304eb4)) }
  .noop_313778 0x00313778 : { KEEP(*(.text.impl.open_cfw_em9305_noop_313778)) }
  .noop_3137f4 0x003137f4 :
  {
    KEEP(*(.text.impl.open_cfw_em9305_noop_3137f4))
    KEEP(*(.text.impl.open_cfw_em9305_noop_3137f8))
  }

  .tail_impl 0x00335bc8 : { KEEP(*(.text.impl.*)) }
  .meta_impl ALIGN(4) :
  {
    KEEP(*(.text.open_cfw_em9305_metaware_memmove))
    KEEP(*(.text.open_cfw_em9305_metaware_memcpy))
    KEEP(*(.text.open_cfw_em9305_metaware_memset))
    KEEP(*(.text.open_cfw_em9305_metaware_udiv64))
    KEEP(*(.text.open_cfw_em9305_metaware_sdiv64))
    KEEP(*(.text.open_cfw_em9305_metaware_shift_left64))
    KEEP(*(.text.open_cfw_em9305_metaware_shift_right64))
    KEEP(*(.text.open_cfw_em9305_metaware_stack_guard))
    *(.text.open_cfw_em9305_shift_left64_words)
    *(.text.open_cfw_em9305_shift_right64_words)
    *(.text.open_cfw_em9305_udivmod64.part.*)
  }

  /DISCARD/ : { *(.comment) *(.note*) *(.ARC.attributes) *(.eh_frame*) }
}

ASSERT(SIZEOF(.tail_303e50) <= 12, "0x303e50 replacement exceeds stock span")
ASSERT(SIZEOF(.tail_303e5c) <= 10, "0x303e5c replacement exceeds stock span")
ASSERT(SIZEOF(.tail_303f50) <= 10, "0x303f50 replacement exceeds stock span")
ASSERT(SIZEOF(.tail_303f68) <= 10, "0x303f68 replacement exceeds stock span")
ASSERT(SIZEOF(.tail_3047b0) <= 14, "0x3047b0 replacement exceeds stock span")
ASSERT(SIZEOF(.tail_3069b8) <= 10, "0x3069b8 replacement exceeds stock span")
ASSERT(SIZEOF(.tail_307c08) <= 14, "0x307c08 replacement exceeds stock span")
ASSERT(SIZEOF(.tail_307dd8) <= 14, "0x307dd8 replacement exceeds stock span")
ASSERT(SIZEOF(.tail_30f368) <= 10, "0x30f368 replacement exceeds stock span")
ASSERT(SIZEOF(.tail_30f710) <= 16, "0x30f710 replacement exceeds stock span")
ASSERT(SIZEOF(.tail_30f720) <= 14, "0x30f720 replacement exceeds stock span")
ASSERT(SIZEOF(.tail_310480) <= 12, "0x310480 replacement exceeds stock span")
ASSERT(SIZEOF(.tail_31048c) <= 10, "0x31048c replacement exceeds stock span")
ASSERT(SIZEOF(.tail_3108f4) <= 10, "0x3108f4 replacement exceeds stock span")
ASSERT(SIZEOF(.tail_311f84) <= 10, "0x311f84 replacement exceeds stock span")
ASSERT(SIZEOF(.tail_3122f0) <= 10, "0x3122f0 replacement exceeds stock span")
ASSERT(SIZEOF(.tail_31369c) <= 14, "0x31369c replacement exceeds stock span")
ASSERT(SIZEOF(.tail_313760) <= 10, "0x313760 replacement exceeds stock span")
ASSERT(SIZEOF(.tail_31b2f8) <= 4, "0x31b2f8 replacement exceeds stock span")
ASSERT(SIZEOF(.tail_32cac4) <= 8, "0x32cac4 replacement exceeds stock span")
ASSERT(SIZEOF(.tail_32cacc) <= 8, "0x32cacc replacement exceeds stock span")
ASSERT(SIZEOF(.tail_32cad4) <= 8, "0x32cad4 replacement exceeds stock span")
ASSERT(SIZEOF(.tail_32cadc) <= 6, "0x32cadc replacement exceeds stock span")
ASSERT(SIZEOF(.meta_302664) == 4, "0x302664 MetaWare entry size drift")
ASSERT(SIZEOF(.meta_302748) == 4, "0x302748 MetaWare entry size drift")
ASSERT(SIZEOF(.meta_302760) == 4, "0x302760 MetaWare entry size drift")
ASSERT(SIZEOF(.meta_3027c8) == 4, "0x3027c8 MetaWare entry size drift")
ASSERT(SIZEOF(.meta_3027f4) == 4, "0x3027f4 MetaWare entry size drift")
ASSERT(SIZEOF(.meta_302820) == 4, "0x302820 MetaWare entry size drift")
ASSERT(SIZEOF(.meta_332fc4) == 4, "0x332fc4 MetaWare entry size drift")
ASSERT(SIZEOF(.meta_33301c) == 4, "0x33301c MetaWare entry size drift")
/* ARC GNU as rounds every input function section to four bytes.  The package
 * builder strips only that trailing section padding after verifying these
 * exact compiler-output sizes. */
ASSERT(SIZEOF(.noop_302d80) == 4, "0x302d80 C no-op section size drift")
ASSERT(SIZEOF(.noop_304eb4) == 8, "0x304eb4 C no-op section size drift")
ASSERT(SIZEOF(.noop_313778) == 4, "0x313778 C no-op section size drift")
ASSERT(SIZEOF(.noop_3137f4) == 8, "0x3137f4 C no-op pair section size drift")
ASSERT(SIZEOF(.tail_impl) <= 1080, "reconstructible implementation cave exceeds sector tail")
ASSERT(ADDR(.meta_impl) + SIZEOF(.meta_impl) <= 0x00336000,
       "combined EM9305 source cave exceeds sector tail")
