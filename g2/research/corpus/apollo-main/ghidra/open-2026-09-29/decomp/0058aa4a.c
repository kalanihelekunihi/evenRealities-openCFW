
int semantic_clamp_window_start(int param_1)

{
  if (*(uint *)(DAT_0058b530 + 0x5190) < 5) {
    param_1 = 0;
  }
  else if (*(uint *)(DAT_0058b530 + 0x5190) < param_1 + 4U) {
    param_1 = *(int *)(DAT_0058b530 + 0x5190) + -4;
  }
  return param_1;
}

