
undefined4 FUN_004815f2(uint param_1,undefined4 param_2)

{
  undefined4 uVar1;
  
  if (((param_1 < 0x38) || (param_1 - 0x3f < 0x3e)) || (0x83 < param_1)) {
    uVar1 = 6;
  }
  else {
    *(undefined4 *)(DAT_004817d8 + (uint)(0x3e < param_1) * -0x3e0 + param_1 * 0x10 + -0x380) =
         param_2;
    uVar1 = 0;
  }
  return uVar1;
}

