
undefined4 FUN_00471e78(int param_1,undefined4 param_2)

{
  undefined4 uVar1;
  
  if ((param_1 == 0xe) || (param_1 == 0xf)) {
    uVar1 = 3;
  }
  else {
    *(undefined4 *)(DAT_00471ed0 + param_1 * 0x20 + 0x20c) = param_2;
    uVar1 = 0;
  }
  return uVar1;
}

