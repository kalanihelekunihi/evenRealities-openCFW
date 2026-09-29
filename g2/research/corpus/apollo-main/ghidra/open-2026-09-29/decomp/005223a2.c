
void FUN_005223a2(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                 undefined4 param_5,undefined4 param_6)

{
  uint *puVar1;
  uint uVar2;
  bool bVar3;
  
  puVar1 = DAT_00522568;
  if ((int)((uint)*(byte *)(*DAT_00522568 + 0x18) << 0x1f) < 0) {
    FUN_005155dc();
  }
  FUN_005155e4(param_1,param_2,param_3,param_4,param_5,param_6);
  uVar2 = *puVar1;
  bVar3 = (*(byte *)(uVar2 + 0x10) & 3) == 0;
  if (bVar3) {
    uVar2 = (uint)*(byte *)(uVar2 + 0x14);
  }
  if (!bVar3 || (uVar2 & 3) != 0) {
    FUN_0051565c(0x2000000);
  }
  return;
}

