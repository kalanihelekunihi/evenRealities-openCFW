
undefined4 syspll_enable_427360(uint *param_1)

{
  undefined4 uVar1;
  byte bVar2;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_004275ac)) {
    uVar1 = 2;
  }
  else if ((int)(*param_1 << 6) < 0) {
    uVar1 = 0;
  }
  else {
    if (((*DAT_004275b0 << 0xc < 0) && (*DAT_004275b0 << 0xd < 0)) && (*DAT_004275b0 << 0xe < 0)) {
      bVar2 = (byte)((uint)(*DAT_004275b0 << 0xf) >> 0x1f) ^ 1;
    }
    else {
      bVar2 = 1;
    }
    if (bVar2 == 0) {
      *DAT_004275b4 = *DAT_004275b4 | 0x20000000;
      *param_1 = *param_1 | 0x2000000;
      uVar1 = 0;
    }
    else {
      uVar1 = 7;
    }
  }
  return uVar1;
}

