
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 hardware_channel_normalize_42eda0(uint *param_1)

{
  uint *puVar1;
  undefined4 uVar2;
  
  puVar1 = _DAT_0042f180;
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != _DAT_0042f17c)) {
    uVar2 = 2;
  }
  else {
    *_DAT_0042f180 = *_DAT_0042f180 & 0xfffffffb;
    *puVar1 = *puVar1 & 0xfffffffe;
    if ((*puVar1 & 0x7ffffff) >> 0x18 == 3) {
      *puVar1 = *puVar1 & 0xf8ffffff;
    }
    clock_release(4,0xf);
    *param_1 = *param_1 & 0xfdffffff;
    uVar2 = 0;
  }
  return uVar2;
}

