
undefined1 * FUN_10009968(undefined1 *param_1,undefined1 *param_2,int param_3)

{
  undefined1 *puVar1;
  
  if (param_2 <= param_1) {
    param_2 = param_2 + param_3;
    puVar1 = param_1 + param_3;
    if (param_3 != 0) {
      do {
        puVar1 = puVar1 + -1;
        param_2 = param_2 + -1;
        *puVar1 = *param_2;
      } while (param_1 != puVar1);
    }
    return param_1;
  }
  FUN_10011344();
  return param_1;
}

