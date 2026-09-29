
undefined4 FUN_00416c4e(int param_1,int *param_2,uint *param_3)

{
  uint uVar1;
  int iVar2;
  
  iVar2 = *param_2;
  uVar1 = -1 << (*param_3 & 0xff) & *(uint *)(param_1 + iVar2 * 4 + 0x14);
  if (uVar1 == 0) {
    uVar1 = -1 << (iVar2 + 1U & 0xff) & *(uint *)(param_1 + 0x10);
    if (uVar1 == 0) {
      return 0;
    }
    iVar2 = FUN_004169e2(uVar1);
    *param_2 = iVar2;
    uVar1 = *(uint *)(param_1 + iVar2 * 4 + 0x14);
  }
  if (uVar1 == 0) {
    FUN_00415734(DAT_004172e0,DAT_00417200,0x238);
  }
  uVar1 = FUN_004169e2(uVar1);
  *param_3 = uVar1;
  return *(undefined4 *)(param_1 + iVar2 * 0x80 + uVar1 * 4 + 0x74);
}

