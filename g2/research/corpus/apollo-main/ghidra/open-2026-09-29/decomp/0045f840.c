
int * FUN_0045f840(int param_1,int param_2)

{
  int *piVar1;
  
  if ((param_1 != 0) && (param_2 != 0)) {
    for (piVar1 = *(int **)(param_1 + 8); piVar1 != (int *)0x0; piVar1 = (int *)piVar1[8]) {
      if (*piVar1 == param_2) {
        return piVar1;
      }
    }
    for (piVar1 = *(int **)(param_1 + 0xc); piVar1 != (int *)0x0; piVar1 = (int *)piVar1[8]) {
      if (*piVar1 == param_2) {
        return piVar1;
      }
    }
  }
  return (int *)0x0;
}

