
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 hw_handle_disable_42ebe2(uint *param_1)

{
  undefined4 uVar1;
  uint uVar2;
  
  uVar2 = param_1[1];
  if ((param_1 == (uint *)0x0) || (uVar2 = _DAT_0042f17c, (*param_1 & 0x1ffffff) != _DAT_0042f17c))
  {
    uVar1 = 2;
  }
  else {
    uVar2 = *_DAT_0042f188 & 0x7fffffff;
    *_DAT_0042f188 = uVar2;
    uVar1 = 0;
  }
  return CONCAT44(uVar2,uVar1);
}

