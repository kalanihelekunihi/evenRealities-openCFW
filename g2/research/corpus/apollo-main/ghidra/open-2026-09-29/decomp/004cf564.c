
void FUN_004cf564(int param_1,byte param_2)

{
  *(uint *)(param_1 + 0x30) = *(uint *)(param_1 + 0x30) & 0xfffffdff | (param_2 & 1) << 9;
  return;
}

