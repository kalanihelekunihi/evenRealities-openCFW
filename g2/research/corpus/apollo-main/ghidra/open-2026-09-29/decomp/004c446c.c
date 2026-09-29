
undefined8 FUN_004c446c(byte param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (param_1 == 4) {
    uVar1 = FUN_004c38a0(param_2,param_3);
    goto LAB_004c449c;
  }
  if (3 < param_1) {
    if (param_1 == 6) {
      uVar1 = FUN_004c3b44(param_2);
      goto LAB_004c449c;
    }
    if (param_1 < 6) {
      uVar1 = FUN_004c399e(param_2);
      goto LAB_004c449c;
    }
  }
  uVar1 = 7;
LAB_004c449c:
  return CONCAT44(unaff_r7,uVar1);
}

