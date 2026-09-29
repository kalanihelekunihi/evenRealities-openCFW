
void FUN_005e1594(int param_1)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  
  iVar3 = *(int *)(param_1 + 0x80);
  piVar4 = (int *)(*(int *)(param_1 + 0xa4) +
                  (*(int *)(param_1 + 0x84) - *(int *)(param_1 + 0x90)) * 4);
  while ((piVar1 = (int *)*piVar4, piVar1 != (int *)0x0 && (*piVar1 <= iVar3))) {
    if (*piVar1 == iVar3) {
      piVar1[2] = *(int *)(param_1 + 0x98) + piVar1[2];
      piVar1[1] = *(int *)(param_1 + 0x9c) + piVar1[1];
      return;
    }
    piVar4 = piVar1 + 3;
  }
  if (*(int *)(param_1 + 0xac) <= *(int *)(param_1 + 0xb0)) {
    FUN_00567790(param_1,1);
  }
  iVar2 = *(int *)(param_1 + 0xb0);
  *(int *)(param_1 + 0xb0) = iVar2 + 1;
  piVar1 = (int *)(iVar2 * 0x10 + *(int *)(param_1 + 0xa8));
  *piVar1 = iVar3;
  piVar1[2] = *(int *)(param_1 + 0x98);
  piVar1[1] = *(int *)(param_1 + 0x9c);
  piVar1[3] = *piVar4;
  *piVar4 = (int)piVar1;
  return;
}

