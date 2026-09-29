
void FUN_0053a414(ushort param_1)

{
  if (-1 < (short)param_1) {
    *(int *)(DAT_0053a654 + ((uint)(int)(short)param_1 >> 5) * 4) = 1 << (param_1 & 0x1f);
  }
  return;
}

