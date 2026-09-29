
undefined4
pt_handler_result(undefined1 param_1,undefined1 param_2,undefined1 param_3,undefined1 *param_4,
                 undefined1 *param_5)

{
  undefined4 uVar1;
  
  if ((param_4 == (undefined1 *)0x0) || (param_5 == (undefined1 *)0x0)) {
    uVar1 = 0xffffffff;
  }
  else {
    *param_4 = param_1;
    param_4[1] = 1;
    param_4[2] = param_3;
    param_4[3] = 1;
    param_4[4] = param_2;
    *param_5 = 5;
    uVar1 = 0;
  }
  return uVar1;
}

