
longlong conversate_ui_menu_focus_callback(void)

{
  int iVar1;
  short *psVar2;
  uint in_r3;
  undefined4 uVar3;
  
  iVar1 = DAT_005b5cc8;
  psVar2 = (short *)FUN_005b43e8(0);
  if (((*(int *)(iVar1 + 0x84) != -1) && (psVar2 != (short *)0x0)) && (*psVar2 != 0)) {
    if (*(int *)(iVar1 + 0x84) == 0) {
      uVar3 = *(undefined4 *)(iVar1 + 0x7c);
    }
    else {
      uVar3 = FUN_0044dce2(*(undefined4 *)(iVar1 + 100),*(int *)(iVar1 + 0x84) + -1);
    }
    FUN_005896fc(*(undefined4 *)(iVar1 + 0x80),uVar3,200);
    *(undefined4 *)(iVar1 + 0x80) = uVar3;
    *(int *)(iVar1 + 0x84) = *(int *)(iVar1 + 0x84) + -1;
  }
  return (ulonglong)in_r3 << 0x20;
}

