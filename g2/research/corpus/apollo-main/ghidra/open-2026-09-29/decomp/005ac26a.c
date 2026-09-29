
bool cff_ps_has_glyph_names(int param_1)

{
  return (*(uint *)(param_1 + 8) & 0x200) != 0;
}

