
undefined4 * get_array_item(int param_1,int param_2)

{
  undefined4 *puVar1;
  
  if (param_1 == 0) {
    puVar1 = (undefined4 *)0x0;
  }
  else {
    puVar1 = *(undefined4 **)(param_1 + 8);
    for (; (puVar1 != (undefined4 *)0x0 && (param_2 != 0)); param_2 = param_2 + -1) {
      puVar1 = (undefined4 *)*puVar1;
    }
  }
  return puVar1;
}

