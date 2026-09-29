
void FUN_00456374(ushort param_1)

{
  if (-1 < (short)param_1) {
    *(int *)(DAT_00456560 + ((uint)(int)(short)param_1 >> 5) * 4) = 1 << (param_1 & 0x1f);
  }
  return;
}

