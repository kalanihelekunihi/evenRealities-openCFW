
undefined8 clock_release(byte param_1,byte param_2)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (param_2 < 0x39) {
    if (param_1 == 0) {
      uVar1 = FUN_00421a62(param_2);
    }
    else if (param_1 == 2) {
      uVar1 = FUN_00421cce(param_2);
    }
    else if (param_1 < 2) {
      uVar1 = FUN_00421ad6(param_2);
    }
    else if (param_1 == 4) {
      uVar1 = FUN_00421e4a(param_2);
    }
    else if (param_1 < 4) {
      uVar1 = FUN_00421b5c(param_2);
    }
    else if (param_1 == 6) {
      uVar1 = FUN_00422220(param_2);
    }
    else if (param_1 < 6) {
      uVar1 = FUN_00422040(param_2);
    }
    else {
      uVar1 = 6;
    }
  }
  else {
    uVar1 = 6;
  }
  return CONCAT44(unaff_r7,uVar1);
}

