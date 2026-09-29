
uint FUN_004893e6(uint *param_1)

{
  byte bVar1;
  uint uVar2;
  
  if ((*param_1 & 0xffff) >> 8 == 0x14) {
    uVar2 = DAT_0048945c & param_1[1] << 1;
  }
  else {
    bVar1 = FUN_00440f44(*param_1 >> 8 & 0xff);
    uVar2 = (uint)bVar1 * (param_1[1] & 0xffff) + 7 >> 3;
  }
  return uVar2;
}

