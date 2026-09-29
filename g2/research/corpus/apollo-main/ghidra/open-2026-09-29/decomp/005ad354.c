
undefined4 cff_parse_font_bbox(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar1 = *(int *)(param_1 + 0x20);
  iVar3 = *(int *)(param_1 + 0x10);
  uVar2 = 0xa1;
  if (*(int *)(param_1 + 0x10) + 0x10U <= *(uint *)(param_1 + 0x14)) {
    cff_parse_fixed(param_1,iVar3);
    uVar2 = FT_RoundFix();
    *(undefined4 *)(iVar1 + 0x54) = uVar2;
    cff_parse_fixed(param_1,iVar3 + 4);
    uVar2 = FT_RoundFix();
    *(undefined4 *)(iVar1 + 0x58) = uVar2;
    cff_parse_fixed(param_1,iVar3 + 8);
    uVar2 = FT_RoundFix();
    *(undefined4 *)(iVar1 + 0x5c) = uVar2;
    cff_parse_fixed(param_1,iVar3 + 0xc);
    uVar2 = FT_RoundFix();
    *(undefined4 *)(iVar1 + 0x60) = uVar2;
    uVar2 = 0;
  }
  return uVar2;
}

