
undefined8 FUN_004222a0(byte param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (param_1 == 4) {
    uVar1 = FUN_004216d4(param_2,param_3);
    goto LAB_004222d0;
  }
  if (3 < param_1) {
    if (param_1 == 6) {
      uVar1 = FUN_00421978(param_2);
      goto LAB_004222d0;
    }
    if (param_1 < 6) {
      uVar1 = FUN_004217d2(param_2);
      goto LAB_004222d0;
    }
  }
  uVar1 = 7;
LAB_004222d0:
  return CONCAT44(unaff_r7,uVar1);
}

