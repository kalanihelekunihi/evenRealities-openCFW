
undefined4 system_close_fifo_push_00469c26(int param_1,ushort param_2)

{
  int iVar1;
  undefined4 uVar2;
  ushort uVar3;
  uint uVar4;
  
  iVar1 = DAT_0046a824;
  if ((param_1 == 0) || (param_2 == 0)) {
    uVar2 = 0xfffffffd;
  }
  else if ((ushort)(0x80U - *(short *)(DAT_0046a824 + 0x84)) < param_2) {
    uVar2 = 0xffffffff;
  }
  else {
    for (uVar3 = 0; uVar3 < param_2; uVar3 = uVar3 + 1) {
      *(undefined1 *)(iVar1 + (uint)*(ushort *)(iVar1 + 0x80)) =
           *(undefined1 *)(param_1 + (uint)uVar3);
      uVar4 = *(ushort *)(iVar1 + 0x80) + 1;
      *(short *)(iVar1 + 0x80) = (short)uVar4 + (short)(uVar4 / 0x80) * -0x80;
      *(short *)(iVar1 + 0x84) = *(short *)(iVar1 + 0x84) + 1;
    }
    uVar2 = 0;
  }
  return uVar2;
}

