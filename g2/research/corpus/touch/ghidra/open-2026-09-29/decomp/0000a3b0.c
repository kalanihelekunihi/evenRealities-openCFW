
undefined4 Cy_SysPm_RegisterCallback(int *param_1)

{
  undefined4 uVar1;
  int *piVar2;
  int *piVar3;
  int iVar4;
  int *piVar5;
  uint uVar6;
  
  if (param_1 == (int *)0x0) {
    uVar1 = 0;
  }
  else if (param_1[3] == 0) {
    uVar1 = 0;
  }
  else if (*param_1 == 0) {
    uVar1 = 0;
  }
  else {
    uVar6 = (uint)*(byte *)(param_1 + 1);
    piVar2 = *(int **)(uVar6 * 4 + DAT_0000a440);
    piVar5 = piVar2;
    if (piVar2 == (int *)0x0) {
      *(int **)(uVar6 * 4 + DAT_0000a440) = param_1;
      param_1[5] = 0;
      param_1[4] = 0;
      uVar1 = 1;
    }
    else {
      while ((piVar3 = (int *)piVar2[5], piVar3 != (int *)0x0 && (piVar2 != param_1))) {
        piVar2 = piVar3;
        if (*(byte *)(piVar3 + 6) <= *(byte *)(param_1 + 6)) {
          piVar5 = piVar3;
        }
      }
      if (piVar2 == param_1) {
        uVar1 = 0;
      }
      else if ((piVar5[4] == 0) && (*(byte *)(param_1 + 6) < *(byte *)(piVar5 + 6))) {
        param_1[5] = (int)piVar5;
        param_1[4] = 0;
        piVar5[4] = (int)param_1;
        *(int **)(uVar6 * 4 + DAT_0000a440) = param_1;
        uVar1 = 1;
      }
      else {
        iVar4 = piVar5[5];
        param_1[5] = iVar4;
        param_1[4] = (int)piVar5;
        if (iVar4 != 0) {
          *(int **)(iVar4 + 0x10) = param_1;
        }
        piVar5[5] = (int)param_1;
        uVar1 = 1;
      }
    }
  }
  return uVar1;
}

