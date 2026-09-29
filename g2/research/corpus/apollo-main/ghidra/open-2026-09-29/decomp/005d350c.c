
undefined4 FUN_005d350c(int param_1)

{
  undefined4 unaff_r7;
  
  *(undefined4 *)(param_1 + 0x10) = 0;
  FT_GlyphLoader_Rewind(*(undefined4 *)(*(int *)(param_1 + 0x1c) + 0xc));
  return unaff_r7;
}

