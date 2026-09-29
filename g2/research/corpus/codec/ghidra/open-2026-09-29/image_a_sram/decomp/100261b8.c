
undefined4 LvpQueuePut(int *param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  undefined4 *puVar4;
  
  puVar4 = param_2;
  if ((*param_1 + param_1[4]) - param_1[3] * ((*param_1 + param_1[4]) / param_1[3]) == param_1[1]) {
    uVar1 = 0;
  }
  else {
    while( true ) {
      iVar3 = param_1[3];
      if (param_1[4] <= (int)puVar4 - (int)param_2) break;
      iVar2 = ((int)puVar4 - (int)param_2) + *param_1;
      *(char *)(param_1[2] + (iVar2 - (iVar2 / iVar3) * iVar3)) = (char)*puVar4;
      puVar4 = (undefined4 *)((int)puVar4 + 1);
    }
    iVar2 = param_1[4] + *param_1;
    *param_1 = iVar2 - (iVar2 / iVar3) * iVar3;
    uVar1 = 1;
  }
  return uVar1;
}

