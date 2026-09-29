
void FUN_005b133c(void)

{
  int iVar1;
  char *pcVar2;
  undefined1 uVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 in_r3;
  
  pcVar2 = DAT_005b1a98;
  iVar1 = DAT_005b15d8;
  *(char *)(DAT_005b15d8 + 0x8c) = *DAT_005b1a98;
  *(char *)(iVar1 + 0x8d) = pcVar2[1];
  if (pcVar2[1] == '\0') {
    uVar4 = 0x120;
  }
  else {
    uVar4 = 0xcc;
  }
  *(undefined4 *)(iVar1 + 0x90) = uVar4;
  if ((pcVar2[2] == '\0') || (*pcVar2 == '\0')) {
    uVar3 = 0;
  }
  else {
    uVar3 = 1;
  }
  *(undefined1 *)(iVar1 + 0x8e) = uVar3;
  *(char *)(iVar1 + 0x94) = pcVar2[4];
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    FUN_0043d574(3,DAT_005b15d0,DAT_005b15cc,DAT_005b1aa0,0x184,DAT_005b1a9c,
                 *(undefined1 *)(iVar1 + 0x8c),*(undefined1 *)(iVar1 + 0x8d),
                 *(undefined4 *)(iVar1 + 0x90),*(undefined1 *)(iVar1 + 0x8e),
                 *(undefined1 *)(iVar1 + 0x94),in_r3);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0xd400000,DAT_005b1aa4,DAT_005b1aa4,*(undefined1 *)(iVar1 + 0x8c),
                        *(undefined1 *)(iVar1 + 0x8d),*(undefined4 *)(iVar1 + 0x90),
                        *(undefined1 *)(iVar1 + 0x8e),*(undefined1 *)(iVar1 + 0x94));
  }
  return;
}

