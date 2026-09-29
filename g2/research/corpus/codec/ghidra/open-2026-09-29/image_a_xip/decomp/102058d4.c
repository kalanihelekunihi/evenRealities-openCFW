
void gx8002_snpu_tcb_init(void)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  
  uVar2 = DAT_1020594c;
  iVar1 = DAT_10205948;
  iVar7 = 0;
  iVar4 = 0;
  do {
    uVar5 = iVar1 + iVar7 + 0x2c;
    iVar3 = 0;
    iVar6 = iVar4 * 0x90;
    iVar9 = 8;
    do {
      iVar8 = iVar1 + iVar6 + iVar3 * 0xc;
      *(uint *)(iVar8 + 0x20) = iVar3 + 0x80U | 0x10000;
      *(uint *)(iVar8 + 0x24) = uVar5 & 0x7ffffff;
      uVar5 = uVar5 + 0xc;
      iVar3 = iVar3 + 1;
      iVar9 = iVar9 + -1;
    } while (iVar9 != 0);
    iVar4 = iVar4 + 1;
    iVar6 = iVar1 + iVar6;
    *(undefined4 *)(iVar6 + 0x80) = 0x88;
    iVar7 = iVar7 + 0x90;
    *(undefined4 *)(iVar6 + 0x10) = uVar2;
  } while (iVar4 != 10);
  return;
}

