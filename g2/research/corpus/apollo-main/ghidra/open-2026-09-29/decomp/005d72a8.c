
undefined4 FUN_005d72a8(uint *param_1,uint *param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  int *piVar5;
  uint uVar6;
  uint uVar7;
  byte *pbVar8;
  uint uVar9;
  uint uVar10;
  
  uVar6 = 0;
  uVar7 = 0;
  pbVar8 = (byte *)param_2[2];
  uVar10 = *param_2;
  uVar9 = 0;
  FUN_005d7106(param_1);
  for (uVar1 = 0; uVar1 < uVar10; uVar1 = uVar1 + 1) {
    if (uVar6 == 0) {
      uVar7 = (uint)*pbVar8;
      pbVar8 = pbVar8 + 1;
      uVar6 = 0x80;
    }
    if ((((uVar7 & uVar6) != 0) &&
        (iVar2 = param_1[2] + uVar1 * 0x1c, -1 < (int)((uint)*(byte *)(iVar2 + 0x10) << 0x1d))) &&
       (*(uint *)(iVar2 + 0x10) = *(uint *)(iVar2 + 0x10) | 4, uVar9 < *param_1)) {
      *(int *)(param_1[3] + uVar9 * 4) = iVar2;
      uVar9 = uVar9 + 1;
    }
    uVar6 = (int)uVar6 >> 1;
  }
  param_1[1] = uVar9;
  uVar1 = param_1[3];
  for (iVar2 = 1; iVar2 < (int)uVar9; iVar2 = iVar2 + 1) {
    piVar4 = *(int **)(uVar1 + iVar2 * 4);
    iVar3 = iVar2;
    while ((iVar3 = iVar3 + -1, -1 < iVar3 &&
           (piVar5 = *(int **)(uVar1 + iVar3 * 4), *piVar4 <= *piVar5))) {
      *(int **)(uVar1 + iVar3 * 4 + 4) = piVar5;
      *(int **)(uVar1 + iVar3 * 4) = piVar4;
    }
  }
  return param_4;
}

