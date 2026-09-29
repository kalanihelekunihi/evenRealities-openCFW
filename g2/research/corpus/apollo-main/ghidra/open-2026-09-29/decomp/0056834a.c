
void FUN_0056834a(uint *param_1,char param_2)

{
  undefined1 uVar1;
  undefined4 *puVar2;
  undefined1 *puVar3;
  undefined1 *puVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 *puVar7;
  undefined4 *puVar8;
  undefined4 uVar9;
  uint uVar10;
  uint uVar11;
  undefined4 *puVar12;
  
  uVar10 = param_1[5];
  if (uVar10 + 1 < *param_1) {
    uVar11 = *param_1 - 1;
    *param_1 = uVar11;
    puVar7 = (undefined4 *)(param_1[2] + uVar11 * 8);
    uVar5 = puVar7[1];
    puVar8 = (undefined4 *)(param_1[2] + uVar10 * 8);
    *puVar8 = *puVar7;
    puVar8[1] = uVar5;
    if (param_2 != '\0') {
      puVar8 = (undefined4 *)(param_1[2] + uVar10 * 8);
      puVar7 = (undefined4 *)(param_1[2] + uVar11 * 8);
      while( true ) {
        puVar12 = puVar7 + -2;
        puVar2 = puVar8 + 2;
        if (puVar12 <= puVar2) break;
        uVar5 = *puVar2;
        uVar6 = puVar8[3];
        uVar9 = puVar7[-1];
        *puVar2 = *puVar12;
        puVar8[3] = uVar9;
        *puVar12 = uVar5;
        puVar7[-1] = uVar6;
        puVar8 = puVar2;
        puVar7 = puVar12;
      }
      puVar3 = (undefined1 *)(param_1[3] + uVar10);
      puVar4 = (undefined1 *)(param_1[3] + uVar11);
      while( true ) {
        puVar4 = puVar4 + -1;
        puVar3 = puVar3 + 1;
        if (puVar4 <= puVar3) break;
        uVar1 = *puVar3;
        *puVar3 = *puVar4;
        *puVar4 = uVar1;
      }
    }
    *(byte *)(param_1[3] + uVar10) = *(byte *)(param_1[3] + uVar10) | 4;
    *(byte *)(param_1[3] + uVar11 + -1) = *(byte *)(param_1[3] + uVar11 + -1) | 8;
  }
  else {
    *param_1 = uVar10;
  }
  param_1[5] = 0xffffffff;
  *(undefined1 *)(param_1 + 4) = 0;
  return;
}

