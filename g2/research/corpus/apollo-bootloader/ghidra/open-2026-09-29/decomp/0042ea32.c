
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 hw_handle_reset_42ea32(uint *param_1)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != _DAT_0042f17c)) {
    uVar1 = 2;
  }
  else {
    *param_1 = *param_1 & 0xfeffffff;
    *param_1 = *param_1 & 0xff000000;
    param_1[1] = 0;
  }
  return uVar1;
}

