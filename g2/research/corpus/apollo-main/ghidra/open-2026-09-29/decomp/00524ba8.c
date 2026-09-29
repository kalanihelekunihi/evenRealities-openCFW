
undefined4 FT_GlyphLoader_Rewind(int param_1)

{
  undefined4 unaff_r7;
  
  *(undefined2 *)(param_1 + 0x16) = 0;
  *(undefined2 *)(param_1 + 0x14) = 0;
  *(undefined4 *)(param_1 + 0x30) = 0;
  FUN_00439c04(param_1 + 0x38,(undefined2 *)(param_1 + 0x14),0x24);
  return unaff_r7;
}

