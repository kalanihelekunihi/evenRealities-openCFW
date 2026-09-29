
undefined8 clock_request(byte param_1,byte param_2)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (param_2 < 0x39) {
    if (param_1 == 0) {
      uVar1 = FUN_00421a30(param_2);
    }
    else if (param_1 == 2) {
      uVar1 = FUN_00421bd2(param_2);
    }
    else if (param_1 < 2) {
      uVar1 = FUN_00421a94(param_2);
    }
    else if (param_1 == 4) {
      uVar1 = FUN_00421d5e(param_2);
    }
    else if (param_1 < 4) {
      uVar1 = FUN_00421b08(param_2);
    }
    else if (param_1 == 6) {
      uVar1 = FUN_004220b2(param_2);
    }
    else if (param_1 < 6) {
      uVar1 = FUN_00421eba(param_2);
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

