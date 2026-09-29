
void FUN_0048b750(uint *param_1,ushort param_2)

{
  *param_1 = *param_1 & 0xffff | ((uint)param_2 | *param_1 >> 0x10) << 0x10;
  return;
}

