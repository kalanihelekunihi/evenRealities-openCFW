
void bl_bounded_sink(undefined4 *param_1,undefined1 param_2)

{
  undefined1 *puVar1;
  
  param_1[2] = param_1[2] + 1;
  if (param_1[1] != 0) {
    puVar1 = (undefined1 *)*param_1;
    *param_1 = puVar1 + 1;
    *puVar1 = param_2;
    param_1[1] = param_1[1] + -1;
  }
  return;
}

