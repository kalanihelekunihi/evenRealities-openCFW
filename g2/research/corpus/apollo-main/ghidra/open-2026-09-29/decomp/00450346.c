
void FUN_00450346(int param_1)

{
  if ((-1 < (int)((uint)*(byte *)(param_1 + 0x14) << 0x1f)) &&
     ((*(byte *)(param_1 + 0x14) & 3) >> 1 != 0)) {
    FUN_004502e0(param_1);
    *(byte *)(param_1 + 0x14) = *(byte *)(param_1 + 0x14) & 0xfd;
  }
  return;
}

