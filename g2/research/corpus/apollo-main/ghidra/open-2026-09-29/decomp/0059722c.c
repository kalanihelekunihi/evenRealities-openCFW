
uint td_bounded_string_copy(undefined1 *param_1,uint param_2,ushort *param_3)

{
  uint uVar1;
  
  if ((param_1 == (undefined1 *)0x0) || (param_2 == 0)) {
    uVar1 = 0;
  }
  else {
    *param_1 = 0;
    if (param_3 == (ushort *)0x0) {
      uVar1 = 0;
    }
    else {
      uVar1 = (uint)*param_3;
      if (param_2 <= uVar1) {
        uVar1 = param_2 - 1;
      }
      if (uVar1 != 0) {
        FUN_00439be4(param_1,param_3 + 1,uVar1);
      }
      param_1[uVar1] = 0;
      uVar1 = uVar1 & 0xffff;
    }
  }
  return uVar1;
}

