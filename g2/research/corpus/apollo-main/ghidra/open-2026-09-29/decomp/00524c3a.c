
void FT_GlyphLoader_Adjust_Points(int param_1)

{
  *(int *)(param_1 + 0x3c) = *(int *)(param_1 + 0x18) + *(short *)(param_1 + 0x16) * 8;
  *(int *)(param_1 + 0x40) = *(int *)(param_1 + 0x1c) + (int)*(short *)(param_1 + 0x16);
  *(int *)(param_1 + 0x44) = *(int *)(param_1 + 0x20) + *(short *)(param_1 + 0x14) * 2;
  if (*(char *)(param_1 + 0x10) != '\0') {
    *(int *)(param_1 + 0x4c) = *(int *)(param_1 + 0x28) + *(short *)(param_1 + 0x16) * 8;
    *(int *)(param_1 + 0x50) = *(int *)(param_1 + 0x2c) + *(short *)(param_1 + 0x16) * 8;
  }
  return;
}

