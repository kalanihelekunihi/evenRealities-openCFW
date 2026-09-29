
undefined8 FUN_00493d02(int param_1,undefined4 param_2,undefined *param_3)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  if (param_1 != 0) {
    iVar4 = 0;
    iVar3 = *(int *)(param_1 + 4);
    while (iVar3 != 0) {
      iVar5 = *(int *)(iVar3 + 4);
      if (*(int *)(iVar3 + 0x10) != 0) {
        bVar1 = *(byte *)(iVar3 + 8);
        if (bVar1 == 0) {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            param_2 = 0x10e;
            param_3 = DAT_004945ec;
            FUN_0043d574(4,DAT_004940c0,DAT_004940bc,DAT_00494470,0x10e,DAT_004945ec,
                         *(undefined4 *)(iVar3 + 0x10));
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_004945f0,DAT_004945f0,*(undefined4 *)(iVar3 + 0x10));
          }
          FUN_004de17c(*(undefined4 *)(iVar3 + 0x10));
          iVar4 = iVar4 + 1;
        }
        else if (bVar1 == 2) {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            param_2 = 0x118;
            param_3 = DAT_00494478;
            FUN_0043d574(4,DAT_004940c0,DAT_004940bc,DAT_00494470,0x118,DAT_00494478,
                         *(undefined4 *)(iVar3 + 0x10));
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_004945e8,DAT_004945e8,*(undefined4 *)(iVar3 + 0x10));
          }
          FUN_004dca3c(*(undefined4 *)(iVar3 + 0x10));
          iVar4 = iVar4 + 1;
        }
        else if (bVar1 < 2) {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            param_2 = 0x113;
            param_3 = DAT_004945f4;
            FUN_0043d574(4,DAT_004940c0,DAT_004940bc,DAT_00494470,0x113,DAT_004945f4,
                         *(undefined4 *)(iVar3 + 0x10));
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_004945f8,DAT_004945f8,*(undefined4 *)(iVar3 + 0x10));
          }
          FUN_004df6ee(*(undefined4 *)(iVar3 + 0x10));
          iVar4 = iVar4 + 1;
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            param_2 = 0x11d;
            param_3 = DAT_0049446c;
            FUN_0043d574(2,DAT_004940c0,DAT_004940bc,DAT_00494470,0x11d,DAT_0049446c,
                         *(undefined1 *)(iVar3 + 8));
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x8400000,DAT_00494474,DAT_00494474,*(undefined1 *)(iVar3 + 8));
          }
        }
        *(undefined4 *)(iVar3 + 0x10) = 0;
      }
      if (*(int *)(iVar3 + 0xc) != 0) {
        file_heap_free(*(undefined4 *)(iVar3 + 0xc));
        *(undefined4 *)(iVar3 + 0xc) = 0;
      }
      file_heap_free(iVar3);
      iVar3 = iVar5;
    }
    *(undefined4 *)(param_1 + 4) = 0;
    *(undefined4 *)(param_1 + 8) = 0;
    *(undefined4 *)(param_1 + 0xc) = 0;
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x132;
      param_3 = PTR_s_evenhub_container_list_destroy__a_004945fc;
      FUN_0043d574(4,DAT_004940c0,DAT_004940bc,DAT_00494470,0x132,
                   PTR_s_evenhub_container_list_destroy__a_004945fc,iVar4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00494828,DAT_00494828,iVar4);
    }
  }
  return CONCAT44(param_3,param_2);
}

