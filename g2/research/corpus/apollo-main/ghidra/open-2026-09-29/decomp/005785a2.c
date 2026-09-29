
undefined4 semantic_CodecParseVersionBytes(byte *param_1,uint *param_2)

{
  undefined4 uVar1;
  
  if ((param_1 == (byte *)0x0) || (param_2 == (uint *)0x0)) {
    uVar1 = 0xffffffff;
  }
  else {
    *param_2 = (uint)param_1[1] << 0x10 | (uint)*param_1 << 0x18 | (uint)param_1[2] << 8 |
               (uint)param_1[3];
    uVar1 = 0;
  }
  return uVar1;
}

