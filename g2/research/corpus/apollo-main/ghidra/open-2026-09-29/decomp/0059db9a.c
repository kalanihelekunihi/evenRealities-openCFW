
void translate_ui_0059db9a(byte param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  char *pcVar5;
  
  if (param_1 < 10) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar2 = translate_ui_0059db80(param_1);
      FUN_0043d574(3,DAT_0059defc,DAT_0059def8,DAT_0059e5e8,0x177,DAT_0059e5f0,param_1,uVar2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      uVar2 = translate_ui_0059db80(param_1);
      compress_log_output(0xc800000,DAT_0059e5f4,DAT_0059e5f4,param_1,uVar2);
    }
    iVar1 = DAT_0059df78;
    if (*(byte *)(DAT_0059df78 + 0x20) < 3) {
      pcVar5 = (char *)(DAT_0059e600 + (uint)*(byte *)(DAT_0059df78 + 0x20) * 0x50 +
                       (uint)param_1 * 8);
      if (*(int *)(pcVar5 + 4) == 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          uVar2 = translate_ui_0059db80(param_1);
          uVar4 = translate_ui_0059db66(*(undefined1 *)(iVar1 + 0x20));
          FUN_0043d574(2,DAT_0059defc,DAT_0059def8,DAT_0059e5e8,0x185,DAT_0059e604,
                       *(undefined1 *)(iVar1 + 0x20),uVar4,param_1,uVar2);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          uVar2 = translate_ui_0059db80(param_1);
          uVar4 = translate_ui_0059db66(*(undefined1 *)(iVar1 + 0x20));
          compress_log_output(0x9000000,DAT_0059e608,DAT_0059e608,*(undefined1 *)(iVar1 + 0x20),
                              uVar4,param_1,uVar2);
        }
      }
      else {
        iVar3 = (**(code **)(pcVar5 + 4))(*(undefined1 *)(DAT_0059df78 + 0x20),param_2);
        if (iVar3 == 0) {
          if (*(char *)(iVar1 + 0x20) != *pcVar5) {
            iVar3 = FUN_0043d0ce();
            if (iVar3 << 0x1e < 0) {
              uVar2 = translate_ui_0059db66(*pcVar5);
              uVar4 = translate_ui_0059db66(*(undefined1 *)(iVar1 + 0x20));
              FUN_0043d574(3,DAT_0059defc,DAT_0059def8,DAT_0059e5e8,0x191,DAT_0059e60c,
                           *(undefined1 *)(iVar1 + 0x20),uVar4,*pcVar5,uVar2);
            }
            iVar3 = FUN_0043d0ce();
            if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
              uVar2 = translate_ui_0059db66(*pcVar5);
              uVar4 = translate_ui_0059db66(*(undefined1 *)(iVar1 + 0x20));
              compress_log_output(0xd000000,DAT_0059e610,DAT_0059e610,*(undefined1 *)(iVar1 + 0x20),
                                  uVar4,*pcVar5,uVar2);
            }
          }
          *(char *)(iVar1 + 0x20) = *pcVar5;
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(1,DAT_0059defc,DAT_0059def8,DAT_0059e5e8,0x195,DAT_0059e614);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_0059e618,DAT_0059e618);
          }
        }
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0059defc,DAT_0059def8,DAT_0059e5e8,0x17b,DAT_0059e5f8,
                     *(undefined1 *)(iVar1 + 0x20));
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_0059e5fc,DAT_0059e5fc,*(undefined1 *)(iVar1 + 0x20));
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0059defc,DAT_0059def8,DAT_0059e5e8,0x173,DAT_0059e5e4,param_1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0059e5ec,DAT_0059e5ec,param_1);
    }
  }
  return;
}

