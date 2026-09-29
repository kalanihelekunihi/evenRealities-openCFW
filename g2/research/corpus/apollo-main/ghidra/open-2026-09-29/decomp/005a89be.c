
int af_glyph_hints_scale_dim(int param_1,char param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = *(uint *)(param_1 + 0x1c);
  uVar3 = uVar2 + *(int *)(param_1 + 0x18) * 0x28;
  if (param_2 == '\0') {
    for (; uVar2 < uVar3; uVar2 = uVar2 + 0x28) {
      iVar1 = FT_MulFix((int)*(short *)(uVar2 + 0xc),param_3);
      *(int *)(uVar2 + 0x10) = param_4 + iVar1;
    }
  }
  else {
    for (; uVar2 < uVar3; uVar2 = uVar2 + 0x28) {
      iVar1 = FT_MulFix((int)*(short *)(uVar2 + 0xe),param_3);
      *(int *)(uVar2 + 0x14) = param_4 + iVar1;
    }
  }
  return param_4;
}

