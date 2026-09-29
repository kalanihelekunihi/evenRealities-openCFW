
undefined4
FUN_005d9118(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  uVar1 = *param_1;
  FUN_005d8f1c(param_1 + 4,uVar1);
  FUN_005d8f1c(param_1 + 0xd,uVar1);
  param_1[1] = 0;
  *param_1 = 0;
  return param_4;
}

