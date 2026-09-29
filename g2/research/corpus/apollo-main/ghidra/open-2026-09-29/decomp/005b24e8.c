
undefined4 FUN_005b24e8(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 in_r3;
  
  iVar3 = DAT_005b2d38;
  iVar2 = FUN_005b0c18();
  if (iVar2 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(3,DAT_005b2d30,DAT_005b2d2c,DAT_005b2d58,0x5d,DAT_005b2d54);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_005b2d5c,DAT_005b2d5c);
    }
    uVar4 = 0;
  }
  else {
    cVar1 = FUN_005897e0();
    if (cVar1 == '\0') {
      if (*(char *)(iVar3 + 0x8c) == '\0') {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(3,DAT_005b2d30,DAT_005b2d2c,DAT_005b2d58,0x69,DAT_005b30a0);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_005b30a4,DAT_005b30a4);
        }
        uVar4 = 0;
      }
      else if (*(int *)(iVar3 + 0x84) < iVar2 + -1) {
        uVar4 = 1;
      }
      else {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(3,DAT_005b2d30,DAT_005b2d2c,DAT_005b2d58,0x6f,DAT_005b30a8,
                       *(undefined4 *)(iVar3 + 0x84),iVar2,in_r3);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0xc800000,DAT_005b3330,DAT_005b3330,*(undefined4 *)(iVar3 + 0x84),
                              iVar2);
        }
        uVar4 = 0;
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(3,DAT_005b2d30,DAT_005b2d2c,DAT_005b2d58,100,DAT_005b2d60);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_005b309c);
      }
      uVar4 = 0;
    }
  }
  return uVar4;
}

