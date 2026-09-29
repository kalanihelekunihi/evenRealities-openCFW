
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 hw_handle_activate_42ed60(uint *param_1)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != _DAT_0042f17c)) {
    uVar1 = 2;
  }
  else if ((int)(*param_1 << 6) < 0) {
    uVar1 = 0;
  }
  else {
    *_DAT_0042f180 = *_DAT_0042f180 | 1;
    *param_1 = *param_1 | 0x2000000;
    uVar1 = 0;
  }
  return uVar1;
}

