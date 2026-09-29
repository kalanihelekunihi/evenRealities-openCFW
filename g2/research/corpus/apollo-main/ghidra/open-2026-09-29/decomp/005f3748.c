
undefined8 tt_delta_shift(int param_1,int param_2,int param_3,int param_4,int param_5)

{
  int iVar1;
  int iVar2;
  
  iVar2 = *(int *)(param_5 + param_3 * 8) - *(int *)(param_4 + param_3 * 8);
  iVar1 = *(int *)(param_5 + param_3 * 8 + 4) - *(int *)(param_4 + param_3 * 8 + 4);
  if ((iVar2 != 0) || (iVar1 != 0)) {
    for (; param_1 < param_3; param_1 = param_1 + 1) {
      *(int *)(param_5 + param_1 * 8) = iVar2 + *(int *)(param_5 + param_1 * 8);
      *(int *)(param_5 + param_1 * 8 + 4) = iVar1 + *(int *)(param_5 + param_1 * 8 + 4);
    }
    while (param_3 = param_3 + 1, param_3 <= param_2) {
      *(int *)(param_5 + param_3 * 8) = iVar2 + *(int *)(param_5 + param_3 * 8);
      *(int *)(param_5 + param_3 * 8 + 4) = iVar1 + *(int *)(param_5 + param_3 * 8 + 4);
    }
  }
  return CONCAT44(iVar1,iVar2);
}

