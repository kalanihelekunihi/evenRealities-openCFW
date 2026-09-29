
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void nvic_enable_bit_430470(ushort param_1)

{
  if (-1 < (short)param_1) {
    *(int *)(_DAT_0043063c + ((uint)(int)(short)param_1 >> 5) * 4) = 1 << (param_1 & 0x1f);
  }
  return;
}

