
void FUN_00598160(undefined4 *param_1,undefined4 param_2,uint param_3)

{
  if ((param_3 & param_3 - 1) != 0) {
    FUN_004d09b4(DAT_00598194,DAT_00598190,9);
  }
  *param_1 = param_2;
  param_1[1] = param_3 - 1;
  param_1[2] = 0;
  param_1[3] = 0;
  return;
}

