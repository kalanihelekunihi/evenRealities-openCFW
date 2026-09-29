
undefined8 FUN_005d7d1c(uint *param_1,int param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint *puVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  int iVar9;
  
  puVar4 = param_1 + param_2 * 10 + 7;
  iVar7 = *(int *)(param_1[param_2 * 10 + 0xf] + 8);
  uVar5 = *(uint *)param_1[param_2 * 10 + 0xf];
  if (param_2 == 0) {
    iVar6 = 1;
  }
  else {
    iVar6 = 2;
  }
  iVar9 = param_2;
  iVar1 = FT_DivFix(0x20,*(undefined4 *)(param_1[6] + param_2 * 0xcc + 200));
  if (0x1e < iVar1) {
    iVar1 = 0x1e;
  }
  if ((1 < uVar5) && (*param_1 != 0)) {
    if (*param_1 < *(uint *)(iVar7 + 0xc)) {
      uVar2 = *param_1;
    }
    else {
      uVar2 = *(uint *)(iVar7 + 0xc);
    }
    for (; 1 < uVar5; uVar5 = uVar5 - 1) {
      if (*(uint *)(iVar7 + 0x1c) < *param_1) {
        uVar8 = *(uint *)(iVar7 + 0x1c);
      }
      else {
        uVar8 = *param_1;
      }
      if (uVar2 < uVar8) {
        param_3 = uVar8 - uVar2;
        uVar3 = param_1[2];
        FUN_005d72a8(puVar4,iVar7 + 0x10);
        iVar9 = iVar6;
        FUN_005d7b62(puVar4,uVar3 + uVar2 * 0x28,param_3,iVar1,iVar6,param_3,param_4);
      }
      uVar2 = uVar8;
      iVar7 = iVar7 + 0x10;
    }
  }
  if (uVar5 == 1) {
    uVar5 = *param_1;
    uVar2 = param_1[2];
    FUN_005d72a8(puVar4,*(undefined4 *)(param_1[param_2 * 10 + 0xf] + 8));
    FUN_005d7b62(puVar4,uVar2,uVar5,iVar1,iVar6,param_3,param_4);
    iVar9 = iVar6;
  }
  uVar2 = param_1[2];
  for (uVar5 = *param_1; uVar5 != 0; uVar5 = uVar5 - 1) {
    if ((*(int *)(uVar2 + 0x18) != 0) && (-1 < (int)((uint)*(byte *)(uVar2 + 0x10) << 0x1b))) {
      *(uint *)(uVar2 + 0x10) = *(uint *)(uVar2 + 0x10) | 0x10;
    }
    uVar2 = uVar2 + 0x28;
  }
  return CONCAT44(param_3,iVar9);
}

