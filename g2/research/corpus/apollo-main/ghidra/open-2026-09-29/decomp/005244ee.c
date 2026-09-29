
uint FT_RoundFix(int param_1)

{
  return (param_1 + 0x8000) - (uint)(param_1 < 0) & 0xffff0000;
}

