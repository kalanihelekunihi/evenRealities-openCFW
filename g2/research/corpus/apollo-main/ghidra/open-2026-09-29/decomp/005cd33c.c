
void FUN_005cd33c(int param_1,uint param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  
  uVar1 = FUN_005ccb5e(param_1,0x50000);
  uVar2 = FUN_005ccb68(param_1,0x50000);
  uVar3 = FUN_005ccb4a(param_1,0x50000);
  uVar4 = FUN_005ccb54(param_1,0x50000);
  uVar5 = FUN_005ccb86(param_1,0x50000);
  uVar6 = FUN_005ccb90(param_1,0x50000);
  uVar7 = FUN_005ccb7c(param_1,0x50000);
  iVar8 = FUN_005ccb36(param_1,0x50000);
  iVar9 = FUN_005ccb40(param_1,0x50000);
  for (; param_2 < *(uint *)(param_1 + 0x30); param_2 = param_2 + 1) {
    iVar11 = FUN_005cd412(param_1,param_2,uVar7,uVar5,uVar6,uVar1,uVar2,uVar3,uVar4);
    iVar12 = iVar9;
    if (iVar11 < iVar9) {
      iVar12 = iVar11;
    }
    iVar10 = iVar8;
    if ((iVar8 <= iVar12) && (iVar10 = iVar11, iVar9 <= iVar11)) {
      iVar10 = iVar9;
    }
    *(int *)(*(int *)(param_1 + 0x38) + param_2 * 4) = iVar10;
  }
  FUN_0043ffa0(param_1);
  FUN_00440656(param_1);
  return;
}

