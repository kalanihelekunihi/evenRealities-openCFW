
void FUN_00554170(byte param_1,undefined4 param_2)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uVar5;
  char *pcVar6;
  
  if (param_1 < 0x13) {
    if (param_1 == 0x12) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uVar3 = FUN_005540d6(0x12);
        FUN_0043d574(4,DAT_00554d3c,DAT_00554d38,DAT_00554c60,0xfb,DAT_00554d44,0x12,uVar3);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        uVar3 = FUN_005540d6(0x12);
        compress_log_output(0x10800000,DAT_00554d48,DAT_00554d48,0x12,uVar3);
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uVar3 = FUN_005540d6(param_1);
        FUN_0043d574(3,DAT_00554d3c,DAT_00554d38,DAT_00554c60,0xfd,DAT_00554d44,param_1,uVar3);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        uVar3 = FUN_005540d6(param_1);
        compress_log_output(0xc800000,DAT_00554d48,DAT_00554d48,param_1,uVar3);
      }
    }
    iVar2 = DAT_00554d28;
    if (*(byte *)(DAT_00554d28 + 0x20) < 4) {
      pcVar6 = (char *)(DAT_00554d54 + (uint)*(byte *)(DAT_00554d28 + 0x20) * 0x98 +
                       (uint)param_1 * 8);
      if (*(int *)(pcVar6 + 4) == 0) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          uVar3 = FUN_005540d6(param_1);
          uVar5 = FUN_005540bc(*(undefined1 *)(iVar2 + 0x20));
          FUN_0043d574(2,DAT_00554d3c,DAT_00554d38,DAT_00554c60,0x10c,DAT_00554e90,
                       *(undefined1 *)(iVar2 + 0x20),uVar5,param_1,uVar3);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          uVar3 = FUN_005540d6(param_1);
          uVar5 = FUN_005540bc(*(undefined1 *)(iVar2 + 0x20));
          compress_log_output(0x9000000,DAT_00554e94,DAT_00554e94,*(undefined1 *)(iVar2 + 0x20),
                              uVar5,param_1,uVar3);
        }
      }
      else {
        iVar4 = (**(code **)(pcVar6 + 4))(*(undefined1 *)(DAT_00554d28 + 0x20),param_2);
        if (iVar4 == 0) {
          cVar1 = *(char *)(iVar2 + 0x20);
          if (cVar1 != *pcVar6) {
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              uVar3 = FUN_005540bc(*pcVar6);
              uVar5 = FUN_005540bc(*(undefined1 *)(iVar2 + 0x20));
              FUN_0043d574(3,DAT_00554d3c,DAT_00554d38,DAT_00554c60,0x11a,DAT_00554e98,
                           *(undefined1 *)(iVar2 + 0x20),uVar5,*pcVar6,uVar3);
            }
            iVar4 = FUN_0043d0ce();
            if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
              uVar3 = FUN_005540bc(*pcVar6);
              uVar5 = FUN_005540bc(*(undefined1 *)(iVar2 + 0x20));
              compress_log_output(0xd000000,DAT_00554ee4,DAT_00554ee4,*(undefined1 *)(iVar2 + 0x20),
                                  uVar5,*pcVar6,uVar3);
            }
          }
          *(char *)(iVar2 + 0x20) = *pcVar6;
          FUN_0058930a(cVar1,*pcVar6);
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(1,DAT_00554d3c,DAT_00554d38,DAT_00554c60,0x121,DAT_00554f28);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_00554f2c,DAT_00554f2c);
          }
        }
      }
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00554d3c,DAT_00554d38,DAT_00554c60,0x102,DAT_00554d4c,
                     *(undefined1 *)(iVar2 + 0x20));
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00554d50,DAT_00554d50,*(undefined1 *)(iVar2 + 0x20));
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00554d3c,DAT_00554d38,DAT_00554c60,0xf6,DAT_00554c5c,param_1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00554c64,DAT_00554c64,param_1);
    }
  }
  return;
}

