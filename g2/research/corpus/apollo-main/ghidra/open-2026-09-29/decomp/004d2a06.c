
byte * DmFindAdType(byte param_1,ushort param_2,byte *param_3)

{
  for (; ((param_2 != 0 && (*param_3 != 0)) && (*param_3 < param_2));
      param_3 = param_3 + *param_3 + 1) {
    if (param_3[1] == param_1) {
      return param_3;
    }
    param_2 = (param_2 - *param_3) - 1;
  }
  return (byte *)0x0;
}

