
int * FUN_005cd638(int param_1,uint param_2,uint param_3,int *param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  *param_4 = 0;
  for (uVar3 = 0; uVar3 < param_3; uVar3 = uVar3 + 1) {
    *param_4 = *(int *)(*(int *)(param_1 + 0x3c) + uVar3 * 4) + *param_4;
  }
  iVar1 = FUN_005ccb9a(param_1,0);
  if (iVar1 == 1) {
    iVar1 = FUN_0044e486(param_1);
    *param_4 = iVar1 + *param_4;
    iVar1 = FUN_0043fd9e(param_1);
    iVar2 = FUN_005ccb68(param_1,0);
    param_4[2] = (iVar1 - *param_4) - iVar2;
    *param_4 = param_4[2] - *(int *)(*(int *)(param_1 + 0x3c) + param_3 * 4);
  }
  else {
    iVar1 = FUN_0044e486(param_1);
    *param_4 = *param_4 - iVar1;
    iVar1 = FUN_005ccb5e(param_1,0);
    *param_4 = iVar1 + *param_4;
    param_4[2] = *(int *)(*(int *)(param_1 + 0x3c) + param_3 * 4) + *param_4 + -1;
  }
  param_4[1] = 0;
  for (uVar3 = 0; uVar3 < param_2; uVar3 = uVar3 + 1) {
    param_4[1] = *(int *)(*(int *)(param_1 + 0x38) + uVar3 * 4) + param_4[1];
  }
  iVar1 = FUN_005ccb4a(param_1,0);
  param_4[1] = iVar1 + param_4[1];
  iVar1 = FUN_0044e498(param_1);
  param_4[1] = param_4[1] - iVar1;
  param_4[3] = *(int *)(*(int *)(param_1 + 0x38) + param_2 * 4) + param_4[1] + -1;
  return param_4;
}

