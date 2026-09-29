
void af_glyph_hints_rescale(int param_1,int param_2)

{
  *(int *)(param_1 + 0xabc) = param_2;
  *(undefined4 *)(param_1 + 0xab4) = *(undefined4 *)(param_2 + 0x1c);
  return;
}

