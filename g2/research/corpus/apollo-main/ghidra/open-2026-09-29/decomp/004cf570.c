
longlong FUN_004cf570(int param_1,char param_2,undefined4 param_3,uint param_4)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  
  iVar2 = FUN_004caeb8(*(undefined4 *)(param_1 + 0x30));
  if ((iVar2 == 0) && (param_2 < '\0')) {
    FUN_004d09b4(DAT_004cfcb0,DAT_004cfa2c,0x131c);
  }
  uVar3 = FUN_004caeb8(*(undefined4 *)(param_1 + 0x30));
  if ((0x1fe < uVar3) && ('\0' < param_2)) {
    FUN_004d09b4(DAT_004cfcb4,DAT_004cfa2c,0x131d);
  }
  *(int *)(param_1 + 0x30) = (int)param_2 + *(int *)(param_1 + 0x30);
  bVar1 = FUN_004caf0c(param_1 + 0x30);
  *(uint *)(param_1 + 0x30) = *(uint *)(param_1 + 0x30) & 0x7fffffff | (uint)bVar1 << 0x1f;
  return (ulonglong)param_4 << 0x20;
}

