
undefined4 Cy_SysTick_SetCallback(uint param_1,undefined4 param_2)

{
  undefined4 uVar1;
  
  if (param_1 < 5) {
    uVar1 = *(undefined4 *)(param_1 * 4 + DAT_0000a6bc);
    *(undefined4 *)(param_1 * 4 + DAT_0000a6bc) = param_2;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

