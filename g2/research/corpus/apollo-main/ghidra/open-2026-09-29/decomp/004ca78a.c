
uint lfs_popc(uint param_1)

{
  uint uVar1;
  
  param_1 = param_1 - (param_1 >> 1 & 0x55555555);
  uVar1 = (param_1 >> 2 & 0x33333333) + (param_1 & 0x33333333);
  return (uVar1 + (uVar1 >> 4) & 0xf0f0f0f) * 0x1010101 >> 0x18;
}

