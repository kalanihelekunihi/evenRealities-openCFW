
undefined4 pt_response_prefix(undefined1 *param_1,undefined1 param_2,undefined1 *param_3)

{
  undefined4 uVar1;
  
  if ((param_1 == (undefined1 *)0x0) || (param_3 == (undefined1 *)0x0)) {
    uVar1 = 0xffffffff;
  }
  else {
    *param_1 = 0x5a;
    param_1[1] = 0xa5;
    param_1[2] = 0xff;
    param_1[3] = param_2;
    *param_3 = 4;
    uVar1 = 0;
  }
  return uVar1;
}

