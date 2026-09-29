
void FUN_004d43f6(int param_1,byte param_2,byte param_3)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  
  bVar1 = param_2 >> 2;
  iVar2 = (param_2 & 3) << 3;
  uVar3 = 0xff << iVar2;
  if (bVar1 < 2) {
    *(uint *)(param_1 + (uint)bVar1 * 4 + 0x30) =
         (uint)param_3 << iVar2 & uVar3 | *(uint *)(param_1 + (uint)bVar1 * 4 + 0x30) & ~uVar3;
  }
  return;
}

