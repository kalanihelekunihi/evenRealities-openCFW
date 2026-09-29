
uint als_function_14(uint param_1)

{
  uint uVar1;
  
  uVar1 = 0;
  while( true ) {
    if (5 < uVar1) {
      return 5;
    }
    if (param_1 <= *(uint *)(DAT_004ae4c8 + uVar1 * 8)) break;
    uVar1 = uVar1 + 1;
  }
  return uVar1;
}

