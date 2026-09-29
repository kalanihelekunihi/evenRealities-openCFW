
void FUN_004506da(int param_1,byte param_2)

{
  *(byte *)(param_1 + 0x5c) = *(byte *)(param_1 + 0x5c) & 0xef | (param_2 & 1) << 4;
  return;
}

