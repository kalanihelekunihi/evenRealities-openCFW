
undefined4 FUN_00559ad2(int param_1)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  char *pcVar7;
  
  if (param_1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00559fb0,DAT_00559fac,DAT_0055a220,0xa1,DAT_0055a21c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0055a224,DAT_0055a224);
    }
    uVar3 = 1;
  }
  else if (*(short *)(param_1 + 2) == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00559fb0,DAT_00559fac,DAT_0055a220,0xa6,DAT_0055a228);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0055a22c,DAT_0055a22c);
    }
    uVar3 = 0;
  }
  else {
    iVar2 = 0;
    health_lock_storage();
    for (iVar6 = 0; iVar6 < (int)(uint)*(ushort *)(param_1 + 2); iVar6 = iVar6 + 1) {
      iVar4 = iVar6 * 0x18 + param_1;
      pcVar7 = (char *)(iVar4 + 4);
      if ((*pcVar7 == '\0') || (*pcVar7 == '\x01')) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(2,DAT_00559fb0,DAT_00559fac,DAT_0055a220,0xb5,DAT_0055a2c4);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x8400000,DAT_0055a2c8,DAT_0055a2c8,iVar6);
        }
      }
      else {
        iVar5 = FUN_00559836(*pcVar7);
        if (iVar5 == 0) {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            FUN_0043d574(2,DAT_00559fb0,DAT_00559fac,DAT_0055a220,0xbc,DAT_0055a2cc,iVar6,*pcVar7);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0x8800000,DAT_0055a2d0,DAT_0055a2d0,iVar6,*pcVar7);
          }
        }
        else {
          cVar1 = FUN_00559d82(pcVar7,iVar5);
          if (cVar1 == '\0') {
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              uVar3 = FUN_00559854(*pcVar7);
              FUN_0043d574(4,DAT_00559fb0,DAT_00559fac,DAT_0055a220,0xc9,DAT_0055a2b4,uVar3,
                           *(undefined4 *)(iVar4 + 8),(double)*(float *)(iVar4 + 0xc),
                           (double)*(float *)(iVar4 + 0x10),*(undefined4 *)(iVar4 + 0x14),
                           *(undefined1 *)(iVar4 + 0x19));
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              uVar3 = FUN_00559854(*pcVar7);
              compress_log_output(0x11800000,DAT_0055a2b8,DAT_0055a2b8,uVar3,
                                  *(undefined4 *)(iVar4 + 8));
            }
            iVar2 = iVar2 + 1;
          }
          else {
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              FUN_0043d574(1,DAT_00559fb0,DAT_00559fac,DAT_0055a220,0xc3,DAT_0055a2bc);
            }
            iVar4 = FUN_0043d0ce();
            if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
              compress_log_output(0x4400000,DAT_0055a2c0,DAT_0055a2c0,iVar6);
            }
          }
        }
      }
    }
    health_unlock_storage();
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(3,DAT_00559fb0,DAT_00559fac,DAT_0055a220,0xd1,DAT_0055a2d4,iVar2,
                   *(undefined2 *)(param_1 + 2));
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0xc800000,DAT_0055a2d8,DAT_0055a2d8,iVar2,*(undefined2 *)(param_1 + 2));
    }
    uVar3 = 0;
  }
  return uVar3;
}

