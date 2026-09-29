
undefined2 cff_get_standard_encoding(uint param_1)

{
  undefined2 uVar1;
  
  if (param_1 < 0x100) {
    uVar1 = *(undefined2 *)(DAT_005ae114 + param_1 * 2);
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

