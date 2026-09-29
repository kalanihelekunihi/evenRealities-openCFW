
int FUN_005e1e7e(int param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  int iVar4;
  int local_18;
  
  local_18 = param_4;
  for (iVar4 = *(int *)(param_1 + 0x90); iVar4 < *(int *)(param_1 + 0x94); iVar4 = iVar4 + 1) {
    iVar1 = *(int *)(param_1 + 0x88);
    iVar2 = 0;
    for (piVar3 = *(int **)(*(int *)(param_1 + 0xa4) + (iVar4 - *(int *)(param_1 + 0x90)) * 4);
        piVar3 != (int *)0x0; piVar3 = (int *)piVar3[3]) {
      if ((iVar2 != 0) && (iVar1 < *piVar3)) {
        local_18 = *piVar3 - iVar1;
        FUN_005e1dce(param_1,iVar1,iVar4,iVar2);
      }
      iVar2 = iVar2 + piVar3[1] * 0x200;
      if ((iVar2 != piVar3[2]) && (*(int *)(param_1 + 0x88) <= *piVar3)) {
        local_18 = 1;
        FUN_005e1dce(param_1,*piVar3,iVar4);
      }
      iVar1 = *piVar3 + 1;
    }
    if (iVar2 != 0) {
      local_18 = *(int *)(param_1 + 0x8c) - iVar1;
      FUN_005e1dce(param_1,iVar1,iVar4,iVar2);
    }
  }
  return local_18;
}

