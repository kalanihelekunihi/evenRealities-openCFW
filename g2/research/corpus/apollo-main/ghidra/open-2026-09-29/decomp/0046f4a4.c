
void FUN_0046f4a4(ushort param_1)

{
  if (-1 < (short)param_1) {
    *(int *)(DAT_00470158 + ((uint)(int)(short)param_1 >> 5) * 4) = 1 << (param_1 & 0x1f);
  }
  return;
}

