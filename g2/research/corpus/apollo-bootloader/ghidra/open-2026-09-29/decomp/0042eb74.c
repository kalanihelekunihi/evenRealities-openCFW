
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 hw_handle_configure_42eb74(uint *param_1,int param_2)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != _DAT_0042f17c)) {
    uVar1 = 2;
  }
  else {
    *_DAT_0042f188 = (*(byte *)(param_2 + 1) & 7) << 0x10 | *(uint *)(param_2 + 4) & 0x3ff;
    uVar1 = 0;
  }
  return uVar1;
}

