
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int system_close_option_position_0046a2ca(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  int *piVar3;
  int *piVar4;
  undefined *puVar5;
  int *piVar6;
  int iVar7;
  int iVar8;
  undefined4 uVar9;
  int iVar10;
  int in_r3;
  int iStack_28;
  
  piVar6 = _DAT_0046ae70;
  piVar4 = DAT_0046acd8;
  piVar3 = DAT_0046acd4;
  puVar2 = _DAT_0046accc;
  iStack_28 = in_r3;
  if (((*_DAT_0046ae70 != 0) && (*DAT_0046acd4 != 0)) && (*DAT_0046acd8 != 0)) {
    FUN_0043f66c(*_DAT_0046accc);
    iStack_28 = FUN_0043fd9e(*piVar6);
    iVar7 = FUN_0043fdda(*piVar6);
    iVar8 = FUN_0043fdda(*piVar3);
    iStack_28 = iStack_28 + *(int *)PTR_DAT_0046acdc * 2;
    FUN_0043f506(*puVar2,iStack_28);
    puVar1 = DAT_0046acc4;
    iStack_28 = *_DAT_0046acd0 + iStack_28;
    FUN_0043f506(*DAT_0046acc4,iStack_28);
    uVar9 = FUN_0044dca2(*puVar1);
    iVar10 = FUN_0043fd9e(uVar9);
    FUN_0043f0e0(*puVar1,(iVar10 - iStack_28) / 2);
    iVar10 = FUN_0043fdda(uVar9);
    FUN_0043f142(*puVar1,(iVar10 - *_DAT_0046acc8) / 2);
    puVar5 = PTR_DAT_0046ace0;
    FUN_0043f6b8(*piVar6,2,0,*(undefined4 *)PTR_DAT_0046ace0);
    iVar7 = *(int *)PTR_DAT_0046ace4 + iVar7 + *(int *)puVar5;
    FUN_0043f6b8(*piVar3,2,0,iVar7);
    FUN_0043f6b8(*piVar4,2,0,*_DAT_0046ae74 + iVar8 + iVar7);
    FUN_0043f66c(*puVar2);
    system_close_update_selection();
  }
  return iStack_28;
}

