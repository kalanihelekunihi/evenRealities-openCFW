
undefined8 FUN_0050fc4e(byte param_1)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if ((*DAT_0050fe7c == '\0') || (3 < param_1)) {
    uVar1 = 0;
  }
  else if (*(int *)(DAT_0050fe9c + (uint)param_1 * 4) == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = FUN_00463e9a(*(undefined4 *)(DAT_0050fe9c + (uint)param_1 * 4));
  }
  return CONCAT44(unaff_r7,uVar1);
}

