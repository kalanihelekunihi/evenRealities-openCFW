
void FT_GlyphLoader_Add(int param_1)

{
  short sVar1;
  short sVar2;
  int iVar3;
  
  if (param_1 != 0) {
    sVar1 = *(short *)(param_1 + 0x38);
    sVar2 = *(short *)(param_1 + 0x16);
    *(short *)(param_1 + 0x16) = *(short *)(param_1 + 0x3a) + *(short *)(param_1 + 0x16);
    *(short *)(param_1 + 0x14) = *(short *)(param_1 + 0x38) + *(short *)(param_1 + 0x14);
    *(int *)(param_1 + 0x30) = *(int *)(param_1 + 0x54) + *(int *)(param_1 + 0x30);
    for (iVar3 = 0; iVar3 < sVar1; iVar3 = iVar3 + 1) {
      *(short *)(*(int *)(param_1 + 0x44) + iVar3 * 2) =
           sVar2 + *(short *)(*(int *)(param_1 + 0x44) + iVar3 * 2);
    }
    FT_GlyphLoader_Prepare();
  }
  return;
}

