
undefined4 gx8002_power_lock(int param_1)

{
  undefined4 uVar1;
  uint uVar2;
  
  uVar2 = 1 << (param_1 - 1U & 0x3f);
  if (((DAT_102077d0[1] & uVar2) == 0) || (0x20 < param_1)) {
    uVar1 = 0xffffffff;
  }
  else {
    *DAT_102077d0 = uVar2 | *DAT_102077d0;
    uVar1 = 0;
  }
  return uVar1;
}

