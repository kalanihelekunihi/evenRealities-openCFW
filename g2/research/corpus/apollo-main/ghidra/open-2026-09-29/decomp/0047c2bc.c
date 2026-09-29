
void FUN_0047c2bc(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int *piVar6;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047c548,DAT_0047c544,DAT_0047cb0c,0x84b,DAT_0047cb08);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_0047cb10);
  }
  iVar1 = DAT_0047cb14;
  iVar3 = 0;
  iVar4 = 0;
  FUN_00475014(0,1);
  for (iVar5 = 0; iVar5 < 10; iVar5 = iVar5 + 1) {
    piVar6 = (int *)(iVar1 + iVar5 * 0x100);
    if ((((*(char *)((int)piVar6 + 0x2f) != '\0') && ((char)piVar6[0xc] != '\0')) && (*piVar6 != -1)
        ) && (*piVar6 != 0)) {
      iVar3 = iVar3 + 1;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0047c548,DAT_0047c544,DAT_0047cb0c,0x85b,DAT_0047cb18,iVar5,
                     *(undefined1 *)((int)piVar6 + 0x2e),*(undefined1 *)((int)piVar6 + 5),
                     (char)piVar6[1],*(undefined1 *)((int)piVar6 + 3),
                     *(undefined1 *)((int)piVar6 + 2),*(undefined1 *)((int)piVar6 + 1),(char)*piVar6
                    );
      }
      iVar2 = FUN_0043d0ce();
      if (-1 < iVar2 << 0x1f) {
        iVar2 = FUN_0043d0ce();
        if (-1 < iVar2 << 0x1d) goto LAB_0047c3d8;
      }
      compress_log_output(0x12000000,DAT_0047cb1c,DAT_0047cb1c,iVar5,
                          *(undefined1 *)((int)piVar6 + 0x2e),*(undefined1 *)((int)piVar6 + 5),
                          (char)piVar6[1],*(undefined1 *)((int)piVar6 + 3),
                          *(undefined1 *)((int)piVar6 + 2),*(undefined1 *)((int)piVar6 + 1),
                          (char)*piVar6);
    }
LAB_0047c3d8:
    iVar4 = iVar4 + 1;
  }
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047c548,DAT_0047c544,DAT_0047cb0c,0x860,DAT_0047cb20,iVar3,iVar4);
  }
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1f < 0) {
LAB_0047c416:
    compress_log_output(0x10800000,DAT_0047cb24,DAT_0047cb24,iVar3,iVar4);
  }
  else {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1d < 0) goto LAB_0047c416;
  }
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047c548,DAT_0047c544,DAT_0047cb0c,0x861,DAT_0047cb28,iVar1);
  }
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1f < 0) {
LAB_0047c45c:
    compress_log_output(0x10400000,DAT_0047cb2c,DAT_0047cb2c,iVar1);
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1d < 0) goto LAB_0047c45c;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047c548,DAT_0047c544,DAT_0047cb0c,0x862,DAT_0047cb30,0x100,0x40);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_0047c4be;
  }
  compress_log_output(0x10800000,DAT_0047cb34,DAT_0047cb34,0x100,0x40);
LAB_0047c4be:
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0047c548,DAT_0047c544,DAT_0047cb0c,0x863,DAT_0047cb38);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_0047cb3c,DAT_0047cb3c);
  }
  return;
}

