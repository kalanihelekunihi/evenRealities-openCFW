
undefined4 FUN_0045fb44(int param_1,int param_2)

{
  undefined4 uVar1;
  int *piVar2;
  
  if ((param_1 == 0) || (param_2 == 0)) {
    uVar1 = 0;
  }
  else {
    for (piVar2 = *(int **)(param_1 + 8); piVar2 != (int *)0x0; piVar2 = (int *)piVar2[8]) {
      if (*piVar2 == param_2) {
        return 0;
      }
    }
    for (piVar2 = *(int **)(param_1 + 0xc); piVar2 != (int *)0x0; piVar2 = (int *)piVar2[8]) {
      if (*piVar2 == param_2) {
        return 0;
      }
    }
    uVar1 = 1;
  }
  return uVar1;
}

