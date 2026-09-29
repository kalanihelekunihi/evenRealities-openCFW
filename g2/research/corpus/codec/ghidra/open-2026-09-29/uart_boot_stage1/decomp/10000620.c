
undefined4 gx8002_uart_stage1_try_get(undefined1 *param_1)

{
  undefined4 uVar1;
  
  if ((((undefined4 *)*piRam1000063c)[5] & 1) == 0) {
    uVar1 = 0xffffffff;
  }
  else {
    *param_1 = (char)*(undefined4 *)*piRam1000063c;
    uVar1 = 0;
  }
  return uVar1;
}

