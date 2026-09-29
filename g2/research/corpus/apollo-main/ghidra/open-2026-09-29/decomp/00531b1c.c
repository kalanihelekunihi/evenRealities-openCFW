
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void AttcInit(void)

{
  int iVar1;
  int iVar2;
  byte bVar3;
  byte bVar4;
  int *piVar5;
  
  iVar1 = DAT_00531bac;
  *(undefined4 *)(DAT_00531bac + 0x1b0) = 0;
  *(undefined1 *)(iVar1 + 0x1b4) = 1;
  for (bVar4 = 0; bVar4 < 3; bVar4 = bVar4 + 1) {
    for (bVar3 = 0; iVar2 = _DAT_00531bcc, bVar3 < 3; bVar3 = bVar3 + 1) {
      piVar5 = (int *)((uint)bVar4 * 0x84 + iVar1 + (uint)bVar3 * 0x2c);
      *piVar5 = _DAT_00531bcc + (uint)bVar4 * 0x14;
      *(undefined1 *)(piVar5 + 9) = *(undefined1 *)(iVar2 + 0x60);
      *(ushort *)(piVar5 + 8) = bVar4 + 1;
      *(byte *)(piVar5 + 10) = bVar3;
      *(byte *)((int)piVar5 + 0x29) = bVar4 + 1;
    }
  }
  *(undefined4 *)(_DAT_00531bcc + 0x3c) = _DAT_00531bd0;
  return;
}

