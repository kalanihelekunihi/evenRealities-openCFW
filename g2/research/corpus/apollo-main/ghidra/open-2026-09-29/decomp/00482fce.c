
undefined4 FUN_00482fce(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  if (param_1[1] != 0) {
    FUN_00482fce(param_1[1],param_2);
  }
  if (*param_1 != 0) {
    (*(code *)*param_1)(param_1,param_2);
  }
  return param_4;
}

