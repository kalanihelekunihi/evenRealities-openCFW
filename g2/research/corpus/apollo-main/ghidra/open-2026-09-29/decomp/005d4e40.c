
undefined8 FUN_005d4e40(int param_1,undefined4 param_2,uint param_3)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 *puVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;
  undefined4 uStack_2c;
  
  iVar1 = *(int *)(param_1 + 0x14) * param_3;
  iVar2 = FUN_005d6e44(param_2);
  iVar2 = iVar2 - iVar1;
  iVar7 = param_3 + iVar2;
  for (uVar8 = 0; uVar8 < param_3; uVar8 = uVar8 + 1) {
    puVar5 = *(undefined4 **)(param_1 + 0x18);
    iVar6 = FUN_005d6f38(param_2,iVar2 + uVar8);
    for (uVar9 = 1; puVar5 = puVar5 + 1, uVar9 < *(uint *)(param_1 + 0x14); uVar9 = uVar9 + 1) {
      uVar3 = FUN_005d6f38(param_2,iVar7);
      iVar7 = iVar7 + 1;
      iVar4 = FT_MulFix(*puVar5,uVar3);
      iVar6 = iVar4 + iVar6;
    }
    FUN_005d6f9e(param_2,iVar2 + uVar8,iVar6);
  }
  FUN_005d6fcc(param_2,iVar1 - param_3);
  return CONCAT44(uStack_2c,iVar1);
}

