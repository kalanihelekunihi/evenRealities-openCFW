
uint system_close_fifo_pop_00469cac(int param_1,ushort param_2)

{
  int iVar1;
  uint uVar2;
  ushort uVar3;
  
  iVar1 = DAT_0046a824;
  if ((param_1 == 0) || (param_2 == 0)) {
    uVar2 = 0xfffffffd;
  }
  else if (*(short *)(DAT_0046a824 + 0x84) == 0) {
    uVar2 = 0;
  }
  else {
    if (*(ushort *)(DAT_0046a824 + 0x84) <= param_2) {
      param_2 = *(ushort *)(DAT_0046a824 + 0x84);
    }
    for (uVar3 = 0; uVar3 < param_2; uVar3 = uVar3 + 1) {
      *(undefined1 *)(param_1 + (uint)uVar3) =
           *(undefined1 *)(iVar1 + (uint)*(ushort *)(iVar1 + 0x82));
      uVar2 = *(ushort *)(iVar1 + 0x82) + 1;
      *(short *)(iVar1 + 0x82) = (short)uVar2 + (short)(uVar2 / 0x80) * -0x80;
      *(short *)(iVar1 + 0x84) = *(short *)(iVar1 + 0x84) + -1;
    }
    uVar2 = (uint)param_2;
  }
  return uVar2;
}

