
void FUN_0041b572(int *param_1,uint *param_2)

{
  int *piVar1;
  
  if (*param_2 == 0xffffffff) {
    piVar1 = (int *)param_1[4];
  }
  else {
    for (piVar1 = param_1 + 2; *(uint *)piVar1[1] <= *param_2; piVar1 = (int *)piVar1[1]) {
    }
  }
  param_2[1] = piVar1[1];
  *(uint **)(param_2[1] + 8) = param_2;
  param_2[2] = (uint)piVar1;
  piVar1[1] = (int)param_2;
  param_2[4] = (uint)param_1;
  *param_1 = *param_1 + 1;
  return;
}

