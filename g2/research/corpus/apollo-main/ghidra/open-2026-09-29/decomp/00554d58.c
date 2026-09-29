
void FUN_00554d58(int param_1,int param_2,int param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  
  iVar3 = DAT_00555754;
  iVar1 = DAT_005553c4;
  if ((((param_1 != 0) && (*(int *)(DAT_005553c4 + 0x10) != 0)) &&
      (*(int *)(DAT_00555754 + 0x18) != 0)) && (iVar2 = FUN_0044dce2(param_1,0), iVar2 != 0)) {
    uVar7 = param_2 * 10 + param_3;
    if (*(uint *)(iVar1 + 0x10) <= uVar7) {
      uVar7 = *(int *)(iVar1 + 0x10) - 1;
    }
    iVar3 = FUN_0043fdda(*(undefined4 *)(iVar3 + 0x18));
    iVar3 = iVar3 / 0x1c;
    iVar4 = FUN_0043fdda(param_1);
    iVar5 = FUN_0043fdda(iVar2);
    uVar6 = *(int *)(iVar1 + 0x10) - iVar3;
    uVar8 = iVar4 - iVar5;
    if ((int)uVar6 < 1) {
      uVar6 = 1;
      uVar7 = 0;
    }
    if ((int)uVar8 < 0) {
      uVar8 = 0;
    }
    uVar9 = (uVar8 * uVar7) / uVar6;
    if ((int)uVar8 < (int)uVar9) {
      uVar9 = uVar8;
    }
    if ((int)uVar9 < 0) {
      uVar9 = 0;
    }
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005558cc,DAT_005558c8,DAT_005558c4,0x2d9,DAT_005558c0,param_2,param_3,uVar7
                   ,*(undefined4 *)(iVar1 + 0x10),iVar3,uVar6,uVar9,uVar8);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x12000000,DAT_005558d0,DAT_005558d0,param_2,param_3,uVar7,
                          *(undefined4 *)(iVar1 + 0x10),iVar3,uVar6,uVar9,uVar8);
    }
    FUN_0043f6b8(iVar2,2,0,uVar9);
  }
  return;
}

