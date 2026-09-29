
undefined4 gx8002_flash_discover(void)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  ushort local_10;
  byte bStack_e;
  
  piVar1 = DAT_10024238;
  uVar5 = 0xffffffff;
  *DAT_10024238 = -1;
  iVar2 = gx8002_flash_command_read(0x9f,&local_10,3);
  if (-1 < iVar2) {
    iVar2 = 0;
    iVar4 = 0;
    while (uVar6 = *(uint *)(DAT_1002423c + iVar2 + 4), uVar6 != 0) {
      iVar2 = iVar2 + 0x18;
      if (uVar6 == (((local_10 & 0xff) << 8 | (local_10 & 0x7fff) >> 8) << 8 | (uint)bStack_e)) {
        *piVar1 = iVar4;
        iVar2 = iVar4 * 0x18 + DAT_1002423c;
        piVar1[1] = *(int *)(iVar2 + 8);
        piVar1[2] = 3;
        piVar1[3] = iVar2;
        break;
      }
      iVar4 = iVar4 + 1;
    }
    if (*piVar1 < 0) {
      iVar2 = 0;
      iVar4 = 0;
      while (iVar3 = *(int *)(DAT_1002423c + iVar2 + 4), iVar3 != 0) {
        iVar2 = iVar2 + 0x18;
        if (iVar3 == DAT_10024240) {
          *piVar1 = iVar4;
          iVar2 = iVar4 * 0x18 + DAT_1002423c;
          piVar1[1] = *(int *)(iVar2 + 8);
          piVar1[2] = 3;
          piVar1[3] = iVar2;
          break;
        }
        iVar4 = iVar4 + 1;
      }
      uVar5 = 0xfffffffe;
    }
    else {
      uVar5 = 0;
    }
  }
  return uVar5;
}

