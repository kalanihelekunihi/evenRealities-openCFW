
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 gx8002_gpio_disable_trigger(uint param_1)

{
  undefined4 uVar1;
  uint uVar2;
  int iVar3;
  
  if (param_1 < 0x20) {
    gx_gpio_set_direction(param_1,2);
    iVar3 = iRam102060cc;
    uVar2 = -2 << (param_1 & 0x3f) | 0xfffffffeU >> 0x20 - (param_1 & 0x3f);
    _DAT_a0001014 = _DAT_a0001014 & uVar2;
    _DAT_a0001018 = _DAT_a0001018 & uVar2;
    _DAT_a0001028 = _DAT_a0001028 & uVar2;
    _DAT_a000102c = _DAT_a000102c & uVar2;
    _DAT_a0001024 = uVar2 & _DAT_a0001024;
    *(undefined4 *)(iRam102060cc + param_1 * 0xc) = 0xff;
    iVar3 = param_1 * 0xc + iVar3;
    uVar1 = 0;
    *(undefined4 *)(iVar3 + 4) = 0;
    *(undefined4 *)(iVar3 + 8) = 0;
  }
  else {
    uVar1 = 0xffffffff;
  }
  return uVar1;
}

