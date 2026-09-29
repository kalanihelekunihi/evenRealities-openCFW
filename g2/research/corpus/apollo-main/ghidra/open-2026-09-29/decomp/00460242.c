
undefined4 FUN_00460242(int param_1,ushort param_2)

{
  int iVar1;
  undefined4 uVar2;
  ushort uVar3;
  uint uVar4;
  
  iVar1 = DAT_00460e04;
  if ((param_1 == 0) || (param_2 == 0)) {
    uVar2 = 0xfffffffd;
  }
  else if ((ushort)(0x100U - *(short *)(DAT_00460e04 + 0x104)) < param_2) {
    uVar2 = 0xffffffff;
  }
  else {
    for (uVar3 = 0; uVar3 < param_2; uVar3 = uVar3 + 1) {
      *(undefined1 *)(iVar1 + (uint)*(ushort *)(iVar1 + 0x100)) =
           *(undefined1 *)(param_1 + (uint)uVar3);
      uVar4 = *(ushort *)(iVar1 + 0x100) + 1;
      *(short *)(iVar1 + 0x100) = (short)uVar4 + (short)(uVar4 / 0x100) * -0x100;
      *(short *)(iVar1 + 0x104) = *(short *)(iVar1 + 0x104) + 1;
    }
    uVar2 = 0;
  }
  return uVar2;
}

