
undefined4
FUN_00482950(undefined4 *param_1,undefined4 param_2,int param_3,undefined4 param_4,
            undefined4 param_5,undefined4 param_6)

{
  FUN_004826fc(param_1,0x14);
  *param_1 = param_2;
  if (param_3 == 0) {
    param_3 = DAT_00482ad4;
  }
  param_1[2] = param_3;
  param_1[3] = param_4;
  param_1[4] = param_5;
  param_1[1] = param_6;
  return param_4;
}

