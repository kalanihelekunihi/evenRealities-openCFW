
undefined4 touch_sub_3084(int param_1)

{
  byte bVar1;
  undefined1 uVar2;
  int iVar3;
  uint uVar4;
  int *piVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  undefined4 uVar9;
  
  piVar5 = *(int **)(param_1 + 0xc);
  uVar9 = 0;
  uVar8 = 0;
  uVar7 = 0;
  while( true ) {
    if (2 < uVar7) {
      return uVar9;
    }
    iVar6 = *piVar5;
    bVar1 = *(byte *)(iVar6 + 0x21);
    uVar4 = (uint)bVar1;
    if (((bVar1 & 4) == 0) && ((uVar4 & 3) != 1)) {
      if ((int)(uVar4 << 0x1c) < 0) {
        uVar2 = touch_sub_2f3c(iVar6,param_1);
        *(undefined1 *)(iVar6 + 0x21) = uVar2;
      }
    }
    else {
      if (*(char *)(iVar6 + 0x38) < '\0') {
        uVar2 = touch_sub_3052(piVar5,param_1);
        *(undefined1 *)(iVar6 + 0x38) = uVar2;
      }
      if ((bVar1 & 4) != 0) {
        uVar2 = touch_sub_2f94(piVar5,param_1);
        *(undefined1 *)(iVar6 + 0x21) = uVar2;
      }
    }
    if (*(char *)((int)piVar5 + 0x7a) == '\x01') {
      uVar8 = 8;
    }
    else if (*(char *)((int)piVar5 + 0x7a) == '\n') {
      uVar8 = 8;
    }
    else {
      uVar9 = 1;
    }
    if ((uVar4 & 3) == 1) {
      iVar3 = touch_sub_2f62(*(byte *)(iVar6 + 0x38) & 0x7f,
                             *(undefined1 *)(*(int *)(param_1 + 8) + 0x4e));
      uVar8 = uVar8 + iVar3;
    }
    if (*(ushort *)(iVar6 + 0xe) < uVar8) break;
    if (0x1000 < *(ushort *)(iVar6 + 0xe)) {
      return 0x800;
    }
    piVar5 = piVar5 + 0x24;
    uVar7 = uVar7 + 1;
  }
  return 0x800;
}

