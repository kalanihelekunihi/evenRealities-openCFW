
undefined4 FUN_005540bc(byte param_1)

{
  undefined4 uVar1;
  
  uVar1 = DAT_00554b18;
  if (param_1 < 4) {
    uVar1 = *(undefined4 *)(DAT_00554d2c + (uint)param_1 * 4);
  }
  return uVar1;
}

