
int FUN_004f6770(void)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  int iVar6;
  undefined4 in_r3;
  int iVar7;
  int iVar8;
  
  iVar8 = 0;
  iVar6 = 0;
  do {
    iVar2 = DAT_004f6d2c;
    if ((int)(uint)*(ushort *)(DAT_004f6d6c + 0x280) <= iVar6) {
      FUN_0043c0e4(DAT_004f6d6c,0x288,0);
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004f6d3c,DAT_004f6d38,DAT_004f6fb0,0x580,DAT_004f6f98,iVar8,
                     *(undefined2 *)(DAT_004f6d2c + 0x280),in_r3);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_004f6fb4,DAT_004f6fb4,iVar8,
                            *(undefined2 *)(DAT_004f6d2c + 0x280));
      }
      return iVar8;
    }
    iVar7 = *(int *)(DAT_004f6d6c + iVar6 * 0x10);
    iVar3 = iVar6 * 0x10 + DAT_004f6d6c;
    uVar4 = *(undefined4 *)(iVar3 + 8);
    uVar5 = *(undefined4 *)(iVar3 + 0xc);
    bVar1 = false;
    for (iVar3 = 0; iVar3 < (int)(uint)*(ushort *)(DAT_004f6d2c + 0x280); iVar3 = iVar3 + 1) {
      if (*(int *)(DAT_004f6d2c + iVar3 * 0x10) == iVar7) {
        iVar3 = DAT_004f6d2c + iVar3 * 0x10;
        *(undefined4 *)(iVar3 + 8) = uVar4;
        *(undefined4 *)(iVar3 + 0xc) = uVar5;
        bVar1 = true;
        break;
      }
    }
    if ((!bVar1) && (*(ushort *)(iVar2 + 0x280) < 0x28)) {
      *(int *)(iVar2 + (uint)*(ushort *)(iVar2 + 0x280) * 0x10) = iVar7;
      iVar3 = (uint)*(ushort *)(iVar2 + 0x280) * 0x10 + iVar2;
      *(undefined4 *)(iVar3 + 8) = uVar4;
      *(undefined4 *)(iVar3 + 0xc) = uVar5;
      *(short *)(iVar2 + 0x280) = *(short *)(iVar2 + 0x280) + 1;
      iVar8 = iVar8 + 1;
    }
    iVar6 = iVar6 + 1;
  } while( true );
}

