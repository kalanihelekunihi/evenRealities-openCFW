
undefined4 FUN_0043e2d4(undefined4 *param_1,undefined4 *param_2)

{
  param_1 = (undefined4 *)*param_1;
  while( true ) {
    if (param_1 == (undefined4 *)0x0) {
      return 0;
    }
    if (param_1 == param_2) break;
    param_1 = (undefined4 *)*param_1;
  }
  return 1;
}

