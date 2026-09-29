
void FUN_005cfaf4(int param_1,char param_2,int *param_3)

{
  int iVar1;
  int *piVar2;
  
  piVar2 = *(int **)(param_1 + 4);
  if (param_2 == '\0') {
    do {
      while (piVar2[3] < 1) {
        FUN_005cf938(piVar2);
      }
      piVar2[3] = 0;
      iVar1 = FUN_005cf938(piVar2);
    } while ((iVar1 == 0) && (piVar2[3] - 1U < 2));
  }
  else {
    do {
      if (piVar2[3] < 2) {
        FUN_005cf99a(piVar2);
      }
      piVar2[3] = 0;
      iVar1 = FUN_005cf938(piVar2);
    } while ((iVar1 == 0) && (piVar2[3] == 2));
  }
  if (param_3 != (int *)0x0) {
    if (iVar1 == 0) {
      iVar1 = 0;
    }
    else {
      iVar1 = (*piVar2 - iVar1) + -1;
    }
    *param_3 = iVar1;
  }
  return;
}

