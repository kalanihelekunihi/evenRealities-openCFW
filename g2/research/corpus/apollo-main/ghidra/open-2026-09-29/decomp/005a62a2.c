
undefined8 af_sort_and_quantize_widths(uint *param_1,int *param_2,int param_3)

{
  uint uVar1;
  int *piVar2;
  int *piVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  int *local_24;
  int iStack_20;
  
  local_24 = param_2;
  iStack_20 = param_3;
  if (*param_1 != 1) {
    for (uVar1 = 1; uVar4 = uVar1, uVar1 < *param_1; uVar1 = uVar1 + 1) {
      for (; (uVar4 != 0 && (param_2[uVar4 * 3] < param_2[uVar4 * 3 + -3])); uVar4 = uVar4 - 1) {
        piVar3 = param_2 + uVar4 * 3;
        local_24 = (int *)*piVar3;
        iStack_20 = piVar3[1];
        iVar6 = piVar3[2];
        piVar3 = param_2 + uVar4 * 3;
        iVar5 = param_2[uVar4 * 3 + -2];
        iVar7 = param_2[uVar4 * 3 + -1];
        *piVar3 = param_2[uVar4 * 3 + -3];
        piVar3[1] = iVar5;
        piVar3[2] = iVar7;
        param_2[uVar4 * 3 + -3] = (int)local_24;
        param_2[uVar4 * 3 + -2] = iStack_20;
        param_2[uVar4 * 3 + -1] = iVar6;
      }
    }
    uVar1 = 0;
    iVar5 = *param_2;
    for (uVar4 = 1; uVar4 < *param_1; uVar4 = uVar4 + 1) {
      if ((param_3 < param_2[uVar4 * 3] - iVar5) || (uVar4 == *param_1 - 1)) {
        iVar6 = 0;
        uVar8 = uVar1;
        if ((param_2[uVar4 * 3] - iVar5 <= param_3) && (uVar4 == *param_1 - 1)) {
          uVar4 = uVar4 + 1;
        }
        for (; uVar8 < uVar4; uVar8 = uVar8 + 1) {
          iVar6 = param_2[uVar8 * 3] + iVar6;
          param_2[uVar8 * 3] = 0;
        }
        param_2[uVar1 * 3] = iVar6 / (int)uVar8;
        if (uVar4 < *param_1 - 1) {
          uVar1 = uVar4 + 1;
          iVar5 = param_2[uVar1 * 3];
        }
      }
    }
    uVar1 = 1;
    for (uVar4 = 1; uVar4 < *param_1; uVar4 = uVar4 + 1) {
      if (param_2[uVar4 * 3] != 0) {
        piVar3 = param_2 + uVar1 * 3;
        piVar2 = param_2 + uVar4 * 3;
        iVar5 = piVar2[1];
        iVar6 = piVar2[2];
        *piVar3 = *piVar2;
        piVar3[1] = iVar5;
        piVar3[2] = iVar6;
        uVar1 = uVar1 + 1;
      }
    }
    *param_1 = uVar1;
  }
  return CONCAT44(iStack_20,local_24);
}

