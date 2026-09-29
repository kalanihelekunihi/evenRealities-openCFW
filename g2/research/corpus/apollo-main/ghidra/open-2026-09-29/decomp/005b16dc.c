
undefined4 FUN_005b16dc(byte param_1)

{
  undefined4 uVar1;
  
  uVar1 = DAT_005b1af4;
  if (param_1 < 7) {
    uVar1 = *(undefined4 *)(DAT_005b1af8 + (uint)param_1 * 4);
  }
  return uVar1;
}

