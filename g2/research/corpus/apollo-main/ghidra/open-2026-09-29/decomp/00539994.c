
undefined4 FUN_00539994(uint *param_1)

{
  undefined4 uVar1;
  byte bVar2;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_00539dac)) {
    uVar1 = 2;
  }
  else if ((int)(*param_1 << 6) < 0) {
    uVar1 = 0;
  }
  else {
    if (((*DAT_00539db0 << 0xc < 0) && (*DAT_00539db0 << 0xd < 0)) && (*DAT_00539db0 << 0xe < 0)) {
      bVar2 = (byte)((uint)(*DAT_00539db0 << 0xf) >> 0x1f) ^ 1;
    }
    else {
      bVar2 = 1;
    }
    if (bVar2 == 0) {
      *DAT_00539db4 = *DAT_00539db4 | 0x20000000;
      *param_1 = *param_1 | 0x2000000;
      uVar1 = 0;
    }
    else {
      uVar1 = 7;
    }
  }
  return uVar1;
}

