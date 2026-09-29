
uint FUN_0058ee58(byte *param_1)

{
  uint uVar1;
  
  uVar1 = (uint)param_1[3];
  if (uVar1 == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = uVar1 - ((uint)param_1[2] * (uint)param_1[2] * 0x366d +
                     (uint)*param_1 * (uint)*param_1 * 0x127c +
                     (uint)param_1[1] * (uint)param_1[1] * 0xb717 >> 0x10) / uVar1 & 0xff;
  }
  return uVar1;
}

