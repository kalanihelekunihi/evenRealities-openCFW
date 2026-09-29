
uint cff_parse_integer(byte *param_1,byte *param_2)

{
  uint uVar1;
  byte *pbVar2;
  
  uVar1 = (uint)*param_1;
  pbVar2 = param_1 + 1;
  if (uVar1 == 0x1c) {
    if (param_1 + 3 <= param_2) {
      return (int)CONCAT11(*pbVar2,param_1[2]);
    }
  }
  else if (uVar1 == 0x1d) {
    if (param_1 + 5 <= param_2) {
      return (uint)param_1[4] |
             (uint)param_1[2] << 0x10 | (uint)*pbVar2 << 0x18 | (uint)param_1[3] << 8;
    }
  }
  else {
    if (uVar1 < 0xf7) {
      return uVar1 - 0x8b;
    }
    if (uVar1 < 0xfb) {
      if (param_1 + 2 <= param_2) {
        return DAT_005ad760 + uVar1 * 0x100 + (uint)*pbVar2;
      }
    }
    else if (param_1 + 2 <= param_2) {
      return ((uVar1 - 0xfb) * -0x100 - (uint)*pbVar2) - 0x6c;
    }
  }
  return 0;
}

