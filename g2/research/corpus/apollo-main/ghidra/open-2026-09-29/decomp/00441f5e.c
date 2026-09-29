
void FUN_00441f5e(undefined4 *param_1,undefined4 param_2)

{
  if (param_1[0x10] != 0) {
    param_1[3] = param_1[3] + param_1[0x10];
    if ((uint)param_1[2] <= (uint)param_1[3]) {
      param_1[3] = *param_1;
    }
    FUN_00439be4(param_2,param_1[3],param_1[0x10]);
  }
  return;
}

