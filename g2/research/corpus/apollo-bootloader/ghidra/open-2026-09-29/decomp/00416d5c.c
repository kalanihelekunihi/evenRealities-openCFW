
void FUN_00416d5c(int param_1,int param_2,uint param_3,uint param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = *(int *)(param_3 * 0x80 + param_1 + param_4 * 4 + 0x74);
  if (iVar3 == 0) {
    FUN_00415734(DAT_004172e8,DAT_00417200,0x261);
  }
  if (param_2 == 0) {
    FUN_00415734(DAT_004172ec,DAT_00417200,0x262);
  }
  *(int *)(param_2 + 8) = iVar3;
  *(int *)(param_2 + 0xc) = param_1;
  *(int *)(iVar3 + 0xc) = param_2;
  iVar3 = FUN_00416a9c(param_2);
  uVar1 = FUN_00416a9c(param_2);
  iVar2 = FUN_00416ba4(uVar1,4);
  if (iVar3 != iVar2) {
    FUN_00415734(DAT_004172f4,DAT_00417200,0x268);
  }
  *(int *)(param_3 * 0x80 + param_1 + param_4 * 4 + 0x74) = param_2;
  *(uint *)(param_1 + 0x10) = *(uint *)(param_1 + 0x10) | 1 << (param_3 & 0xff);
  *(uint *)(param_1 + param_3 * 4 + 0x14) =
       1 << (param_4 & 0xff) | *(uint *)(param_1 + param_3 * 4 + 0x14);
  return;
}

