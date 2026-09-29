
uint FUN_100029c0(uint param_1)

{
  if (param_1 < 0x20000000) {
    param_1 = param_1 & 0x7ffffff;
  }
  return param_1;
}

