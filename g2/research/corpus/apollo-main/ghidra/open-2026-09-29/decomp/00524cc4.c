
void FT_GlyphLoader_Adjust_Subglyphs(int param_1)

{
  *(int *)(param_1 + 0x58) = *(int *)(param_1 + 0x30) * 0x20 + *(int *)(param_1 + 0x34);
  return;
}

