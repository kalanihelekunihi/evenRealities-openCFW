
undefined4 SmpDbService(void)

{
  int *piVar1;
  int iVar2;
  undefined4 in_r3;
  byte bVar3;
  int iVar4;
  
  iVar4 = DAT_005429f4;
  for (bVar3 = 0; bVar3 < 10; bVar3 = bVar3 + 1) {
    iVar2 = smpDbRecordInUse(iVar4);
    if (iVar2 != 0) {
      if (*(uint *)(iVar4 + 0x10) < 0x3e9) {
        iVar2 = 0;
      }
      else {
        iVar2 = *(int *)(iVar4 + 0x10) + -1000;
      }
      *(int *)(iVar4 + 0x10) = iVar2;
      if (*(uint *)(iVar4 + 0xc) < 0x3e9) {
        iVar2 = 0;
      }
      else {
        iVar2 = *(int *)(iVar4 + 0xc) + -1000;
      }
      *(int *)(iVar4 + 0xc) = iVar2;
      if (*(uint *)(iVar4 + 0x14) < 0x3e9) {
        iVar2 = 0;
      }
      else {
        iVar2 = *(int *)(iVar4 + 0x14) + -1000;
      }
      *(int *)(iVar4 + 0x14) = iVar2;
      piVar1 = DAT_00542a28;
      if (*(int *)(iVar4 + 0x10) == 0) {
        *(ushort *)(iVar4 + 8) = *(ushort *)(iVar4 + 8) / *(ushort *)(*DAT_00542a28 + 0x14);
        if (*(short *)(iVar4 + 8) != 0) {
          *(undefined4 *)(iVar4 + 0x10) = *(undefined4 *)(*piVar1 + 0x10);
        }
      }
      if (*(int *)(iVar4 + 0x14) == 0) {
        *(undefined1 *)(iVar4 + 7) = 0;
      }
      iVar2 = smpDbRecordInUse(iVar4);
      if (iVar2 != 0) {
        smpDbStartServiceTimer();
      }
    }
    iVar4 = iVar4 + 0x18;
  }
  return in_r3;
}

