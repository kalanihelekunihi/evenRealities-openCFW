
void _iup_worker_shift(int *param_1,uint param_2,uint param_3,uint param_4)

{
  int iVar1;
  
  iVar1 = *(int *)(param_1[1] + param_4 * 8) - *(int *)(*param_1 + param_4 * 8);
  if (iVar1 != 0) {
    for (; param_2 < param_4; param_2 = param_2 + 1) {
      *(int *)(param_1[1] + param_2 * 8) = iVar1 + *(int *)(param_1[1] + param_2 * 8);
    }
    while (param_4 = param_4 + 1, param_4 <= param_3) {
      *(int *)(param_1[1] + param_4 * 8) = iVar1 + *(int *)(param_1[1] + param_4 * 8);
    }
  }
  return;
}

