
undefined8 FUN_004c44bc(byte param_1,byte param_2)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (param_2 < 0x39) {
    if (param_1 == 0) {
      uVar1 = FUN_004c3bfc(param_2);
    }
    else if (param_1 == 2) {
      uVar1 = FUN_004c3d9e(param_2);
    }
    else if (param_1 < 2) {
      uVar1 = FUN_004c3c60(param_2);
    }
    else if (param_1 == 4) {
      uVar1 = FUN_004c3f2a(param_2);
    }
    else if (param_1 < 4) {
      uVar1 = FUN_004c3cd4(param_2);
    }
    else if (param_1 == 6) {
      uVar1 = FUN_004c427e(param_2);
    }
    else if (param_1 < 6) {
      uVar1 = FUN_004c4086(param_2);
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

