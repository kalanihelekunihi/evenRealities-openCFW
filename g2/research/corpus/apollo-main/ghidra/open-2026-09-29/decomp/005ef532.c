
undefined4 TT_Forget_Glyph_Frame(int param_1)

{
  undefined4 unaff_r7;
  
  FT_Stream_ExitFrame(*(undefined4 *)(param_1 + 0x18));
  return unaff_r7;
}

