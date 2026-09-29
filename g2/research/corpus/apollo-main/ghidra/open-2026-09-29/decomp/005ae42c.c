
void cff_blend_clear(int param_1)

{
  *(undefined4 *)(param_1 + 0x254) = *(undefined4 *)(param_1 + 0x250);
  *(undefined4 *)(param_1 + 600) = 0;
  return;
}

