
void FUN_00456358(ushort param_1)

{
  if (-1 < (short)param_1) {
    *(int *)(DAT_0045655c + ((uint)(int)(short)param_1 >> 5) * 4) = 1 << (param_1 & 0x1f);
  }
  return;
}

