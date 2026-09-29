
uint FUN_004d3a38(byte param_1)

{
  return (uint)param_1 % 10 | (param_1 / 10 & 0xf) << 4;
}

