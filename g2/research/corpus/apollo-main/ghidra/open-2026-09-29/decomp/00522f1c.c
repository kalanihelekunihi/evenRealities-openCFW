
uint FUN_00522f1c(float param_1)

{
  int iVar1;
  
  iVar1 = (int)(param_1 * DAT_00523280 + 0.5);
  if (0x60 < iVar1) {
    return 0x60;
  }
  if (iVar1 < 0x20) {
    return 0x20;
  }
  return iVar1 + 0xf + ((uint)(iVar1 + 0xf >> 3) >> 0x1c) & 0xfffffff0;
}

