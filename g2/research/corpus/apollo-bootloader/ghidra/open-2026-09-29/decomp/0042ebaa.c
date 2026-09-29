
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 hw_handle_enable_42ebaa(uint *param_1)

{
  undefined4 uVar1;
  uint uVar2;
  
  uVar2 = param_1[1];
  if ((param_1 == (uint *)0x0) || (uVar2 = _DAT_0042f17c, (*param_1 & 0x1ffffff) != _DAT_0042f17c))
  {
    uVar1 = 2;
  }
  else if (*_DAT_0042f180 << 0x1f < 0) {
    uVar2 = *_DAT_0042f188;
    *_DAT_0042f188 = uVar2 | 0x80000000;
    uVar1 = 0;
    uVar2 = uVar2 | 0x80000000;
  }
  else {
    uVar1 = 7;
  }
  return CONCAT44(uVar2,uVar1);
}

