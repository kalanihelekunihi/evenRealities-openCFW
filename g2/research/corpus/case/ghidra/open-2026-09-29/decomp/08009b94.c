
uint case_hex_value(int param_1)

{
  byte bVar1;
  
  if (param_1 - 0x30U < 10) {
    return param_1 - 0x30U & 0xff;
  }
  if (param_1 - 0x61U < 6) {
    bVar1 = (char)param_1 + 0xa9;
  }
  else {
    if (5 < param_1 - 0x41U) {
      return 0;
    }
    bVar1 = (char)param_1 - 0x37;
  }
  return (uint)bVar1;
}

