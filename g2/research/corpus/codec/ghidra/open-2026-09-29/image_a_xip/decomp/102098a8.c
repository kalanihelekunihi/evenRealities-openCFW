
uint crc32(uint param_1)

{
  uint uVar1;
  
  uVar1 = crc32_no_comp(~param_1);
  return ~uVar1;
}

