
void FUN_0045028e(int param_1)

{
  int *piVar1;
  
  for (piVar1 = *(int **)(DAT_004502b4 + 0x6c); piVar1 != (int *)0x0; piVar1 = (int *)piVar1[5]) {
    if ((piVar1[1] == param_1) || (*piVar1 == param_1)) {
      *(byte *)(piVar1 + 6) = *(byte *)(piVar1 + 6) | 1;
    }
  }
  return;
}

