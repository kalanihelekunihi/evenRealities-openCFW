
uint case_shift_selected(void)

{
  return *DAT_08005490 >>
         (*(byte *)(DAT_08005498 + ((*(uint *)(DAT_08005494 + 8) & 0x7fff) >> 0xc) * 4) & 0x1f);
}

