
void FUN_00500f00(void)

{
  char *pcVar1;
  int iVar2;
  undefined4 in_r3;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  pcVar1 = DAT_00501168;
  if (*DAT_00501168 == '\0') {
    return;
  }
  if (*(int *)(DAT_00501168 + 0x14) != *(int *)(DAT_00501168 + 8)) {
    return;
  }
  uStack_c = in_r3;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    uStack_10 = *(undefined4 *)(pcVar1 + 0x18);
    uStack_14 = *(undefined4 *)(pcVar1 + 8);
    uStack_18 = *(undefined4 *)(pcVar1 + 4);
    uStack_1c = DAT_005017f8;
    FUN_0043d574(3,DAT_00501188,DAT_00501184,DAT_005017fc,0x1ac);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    uStack_1c = *(undefined4 *)(pcVar1 + 0x18);
    compress_log_output(0xcc00000,DAT_00501800,DAT_00501800,*(undefined4 *)(pcVar1 + 4),
                        *(undefined4 *)(pcVar1 + 8));
  }
  if (*(int *)(pcVar1 + 0xc) != 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uStack_18 = *(undefined4 *)(pcVar1 + 0xc);
      uStack_1c = DAT_00501804;
      FUN_0043d574(2,DAT_00501188,DAT_00501184,DAT_005017fc,0x1b4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_00501808,DAT_00501808,*(undefined4 *)(pcVar1 + 0xc));
    }
    FUN_00500824();
    FUN_00500bf4(0);
    return;
  }
  iVar2 = FUN_00500cb0(pcVar1 + 0x1c,*(undefined4 *)(pcVar1 + 0x14));
  FUN_00500824();
  if (iVar2 != 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uStack_1c = DAT_0050180c;
      FUN_0043d574(1,DAT_00501188,DAT_00501184,DAT_005017fc,0x1c1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00501810,DAT_00501810);
    }
    FUN_00500bf4(0);
    return;
  }
  FUN_00501d5c();
  iVar2 = FUN_0045a568();
  if (iVar2 != 2) {
    return;
  }
  FUN_00454b4c(100);
  FUN_0043c0e4(&uStack_1c,6,0);
  FUN_0043c0e4(&uStack_1c,6,0);
  uStack_1c = CONCAT31(uStack_1c._1_3_,1);
  FUN_00465480(0x1f,&uStack_1c,6,0,5);
  return;
}

