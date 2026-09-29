
undefined8 FUN_004c4530(byte param_1,byte param_2)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (param_2 < 0x39) {
    if (param_1 == 0) {
      uVar1 = FUN_004c3c2e(param_2);
    }
    else if (param_1 == 2) {
      uVar1 = FUN_004c3e9a(param_2);
    }
    else if (param_1 < 2) {
      uVar1 = FUN_004c3ca2(param_2);
    }
    else if (param_1 == 4) {
      uVar1 = FUN_004c4016(param_2);
    }
    else if (param_1 < 4) {
      uVar1 = FUN_004c3d28(param_2);
    }
    else if (param_1 == 6) {
      uVar1 = FUN_004c43ec(param_2);
    }
    else if (param_1 < 6) {
      uVar1 = FUN_004c420c(param_2);
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

