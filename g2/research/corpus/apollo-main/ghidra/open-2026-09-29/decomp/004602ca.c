
uint FUN_004602ca(int param_1,ushort param_2)

{
  int iVar1;
  uint uVar2;
  ushort uVar3;
  
  iVar1 = DAT_00460e04;
  if ((param_1 == 0) || (param_2 == 0)) {
    uVar2 = 0xfffffffd;
  }
  else if (*(short *)(DAT_00460e04 + 0x104) == 0) {
    uVar2 = 0;
  }
  else {
    if (*(ushort *)(DAT_00460e04 + 0x104) <= param_2) {
      param_2 = *(ushort *)(DAT_00460e04 + 0x104);
    }
    for (uVar3 = 0; uVar3 < param_2; uVar3 = uVar3 + 1) {
      *(undefined1 *)(param_1 + (uint)uVar3) =
           *(undefined1 *)(iVar1 + (uint)*(ushort *)(iVar1 + 0x102));
      uVar2 = *(ushort *)(iVar1 + 0x102) + 1;
      *(short *)(iVar1 + 0x102) = (short)uVar2 + (short)(uVar2 / 0x100) * -0x100;
      *(short *)(iVar1 + 0x104) = *(short *)(iVar1 + 0x104) + -1;
    }
    uVar2 = (uint)param_2;
  }
  return uVar2;
}

