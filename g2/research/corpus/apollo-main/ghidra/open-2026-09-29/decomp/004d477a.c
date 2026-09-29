
undefined8
FUN_004d477a(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 local_10;
  
  uVar1 = FUN_004416d6(4);
  param_1[1] = uVar1;
  if (param_1[1] == 0) {
    local_10 = DAT_004d47c4;
    FUN_0044d25c(3,DAT_004d47b0,0x1ba,DAT_004d47c8);
  }
  else {
    *param_1 = 1;
    local_10 = param_3;
  }
  return CONCAT44(param_4,local_10);
}

