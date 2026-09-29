
void FT_GlyphLoader_Prepare(int param_1)

{
  *(undefined2 *)(param_1 + 0x3a) = 0;
  *(undefined2 *)(param_1 + 0x38) = 0;
  *(undefined4 *)(param_1 + 0x54) = 0;
  FT_GlyphLoader_Adjust_Points(param_1);
  FT_GlyphLoader_Adjust_Subglyphs(param_1);
  return;
}

