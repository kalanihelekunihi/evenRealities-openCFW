
int FUN_005d13c4(int param_1)

{
  int iVar1;
  short *psVar2;
  
  psVar2 = *(short **)(param_1 + 0x14);
  if (psVar2 == (short *)0x0) {
    iVar1 = 3;
  }
  else if (*(char *)(param_1 + 0x41) == '\0') {
    *psVar2 = *psVar2 + 1;
    iVar1 = 0;
  }
  else {
    if (*(uint *)(*(int *)(param_1 + 0xc) + 8) <
        (int)*(short *)(*(int *)(param_1 + 0xc) + 0x38) +
        (int)*(short *)(*(int *)(param_1 + 0xc) + 0x14) + 1U) {
      iVar1 = FT_GlyphLoader_CheckPoints(*(undefined4 *)(param_1 + 0xc),0,1);
    }
    else {
      iVar1 = 0;
    }
    if (iVar1 == 0) {
      if (0 < *psVar2) {
        *(short *)(*(int *)(psVar2 + 6) + *psVar2 * 2 + -2) = psVar2[1] + -1;
      }
      *psVar2 = *psVar2 + 1;
    }
  }
  return iVar1;
}

