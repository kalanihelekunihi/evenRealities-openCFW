
void FUN_005d0574(int *param_1,int param_2)

{
  int iVar1;
  int *piVar2;
  int *piVar3;
  
  iVar1 = *param_1;
  piVar2 = (int *)param_1[6];
  piVar3 = piVar2 + param_1[4];
  for (; piVar2 < piVar3; piVar2 = piVar2 + 1) {
    if (*piVar2 != 0) {
      *piVar2 = *piVar2 + (iVar1 - param_2);
    }
  }
  return;
}

