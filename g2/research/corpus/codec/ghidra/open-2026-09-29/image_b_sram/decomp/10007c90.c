
undefined4 FUN_10007c90(void)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  uint uVar4;
  uint *puVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  ushort local_10;
  byte bStack_e;
  
  piVar2 = DAT_10007d68;
  *DAT_10007d68 = -1;
  iVar3 = FUN_10006c30(0x9f,&local_10,3);
  if (iVar3 < 0) {
    return 0xffffffff;
  }
  uVar8 = *(uint *)(DAT_10007d6c + 4);
  uVar4 = ((local_10 & 0xff) << 8 | (local_10 & 0x7fff) >> 8) << 8 | (uint)bStack_e;
  if (uVar8 == 0) {
    if (*piVar2 < 0) {
      return 0xfffffffe;
    }
  }
  else {
    if (uVar8 == uVar4) {
      iVar3 = 0;
      iVar6 = DAT_10007d6c;
    }
    else {
      puVar5 = (uint *)(DAT_10007d6c + 0x1c);
      iVar3 = 0;
      do {
        uVar7 = *puVar5;
        iVar3 = iVar3 + 1;
        if (uVar7 == 0) {
          if (-1 < *piVar2) {
            return 0;
          }
          if (uVar8 == DAT_10007d70) {
            iVar3 = 0;
            iVar6 = DAT_10007d6c;
          }
          else {
            iVar3 = 0;
            puVar5 = DAT_10007d74;
            do {
              uVar4 = *puVar5;
              iVar3 = iVar3 + 1;
              if (uVar4 == 0) {
                return 0xfffffffe;
              }
              puVar5 = puVar5 + 6;
            } while (uVar4 != DAT_10007d70);
            iVar6 = iVar3 * 0x18 + DAT_10007d6c;
          }
          iVar1 = DAT_10007d6c + iVar3 * 0x18;
          *piVar2 = iVar3;
          piVar2[1] = *(int *)(iVar1 + 8);
          piVar2[2] = 3;
          piVar2[3] = iVar6;
          return 0xfffffffe;
        }
        puVar5 = puVar5 + 6;
      } while (uVar7 != uVar4);
      iVar6 = iVar3 * 0x18 + DAT_10007d6c;
    }
    iVar1 = DAT_10007d6c + iVar3 * 0x18;
    *piVar2 = iVar3;
    piVar2[1] = *(int *)(iVar1 + 8);
    piVar2[2] = 3;
    piVar2[3] = iVar6;
  }
  return 0;
}

