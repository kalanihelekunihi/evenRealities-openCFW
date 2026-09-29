
undefined8 FT_Render_Glyph(int param_1,undefined1 param_2)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if ((param_1 == 0) || (*(int *)(param_1 + 4) == 0)) {
    uVar1 = 6;
  }
  else {
    uVar1 = FT_Render_Glyph_Internal
                      (*(undefined4 *)(*(int *)(*(int *)(param_1 + 4) + 0x60) + 4),param_1,param_2);
  }
  return CONCAT44(unaff_r7,uVar1);
}

