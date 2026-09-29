
undefined4 FUN_005d185e(int param_1,int param_2)

{
  undefined4 uVar1;
  
  if ((param_2 == 0) ||
     ((uint)(param_2 +
            (int)*(short *)(*(int *)(param_1 + 0xc) + 0x3a) +
            (int)*(short *)(*(int *)(param_1 + 0xc) + 0x16)) <=
      *(uint *)(*(int *)(param_1 + 0xc) + 4))) {
    uVar1 = 0;
  }
  else {
    uVar1 = FT_GlyphLoader_CheckPoints(*(undefined4 *)(param_1 + 0xc),param_2,0);
  }
  return uVar1;
}

