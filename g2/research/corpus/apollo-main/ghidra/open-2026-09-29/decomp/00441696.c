
undefined4
FUN_00441696(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4,
            undefined4 *param_5)

{
  if (param_2 == 0) {
    *param_5 = param_5;
  }
  else {
    *param_5 = param_3;
  }
  param_5[0xf] = param_1;
  param_5[0x10] = param_2;
  FUN_00441516(param_5,1);
  *(char *)(param_5 + 0x13) = (char)param_4;
  return param_4;
}

