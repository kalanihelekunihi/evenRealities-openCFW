
void case_advance_cursor(undefined4 *param_1,undefined4 param_2)

{
  uint uVar1;
  
  if (param_1[0x10] != 0) {
    uVar1 = param_1[3] + param_1[0x10];
    param_1[3] = uVar1;
    if ((uint)param_1[2] <= uVar1) {
      param_1[3] = *param_1;
    }
    FUN_080001b4(param_2,param_1[3]);
  }
  return;
}

