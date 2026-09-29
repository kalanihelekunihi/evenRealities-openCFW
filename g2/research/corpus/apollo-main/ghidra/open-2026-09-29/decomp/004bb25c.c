
undefined8 FUN_004bb25c(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  if ((param_1 & 0xff) == 0) {
    uVar2 = param_1;
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004bb3a0,&DAT_004bb39c,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004bb3a0,DAT_004bb3a0,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004bb3a0,DAT_004bb3a8,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_004bb394,&DAT_004bb398,3), iVar1 != 0)) {
              WsfTrace(DAT_004bb3a0,DAT_004bb3d4,param_1 & 0xff);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              uVar2 = 0x22c;
              param_2 = DAT_004bb3d4;
              FUN_0043d574(4,&DAT_004bb394,DAT_004bb3a4,DAT_004bb3d8,0x22c,DAT_004bb3d4,
                           param_1 & 0xff);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            uVar2 = 0x22c;
            param_2 = DAT_004bb3d4;
            FUN_0043d574(3,&DAT_004bb394,DAT_004bb3a4,DAT_004bb3d8,0x22c,DAT_004bb3d4,param_1 & 0xff
                        );
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          uVar2 = 0x22c;
          param_2 = DAT_004bb3d4;
          FUN_0043d574(2,&DAT_004bb394,DAT_004bb3a4,DAT_004bb3d8,0x22c,DAT_004bb3d4,param_1 & 0xff);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar2 = 0x22c;
        param_2 = DAT_004bb3d4;
        FUN_0043d574(1,&DAT_004bb394,DAT_004bb3a4,DAT_004bb3d8,0x22c,DAT_004bb3d4,param_1 & 0xff,
                     param_4);
      }
    }
  }
  else {
    iVar1 = DAT_004bb3ac + (param_1 & 0xff) * 0x30;
    *(undefined1 *)(iVar1 + -4) = *DAT_004bb3b8;
    *(undefined1 *)(iVar1 + -6) = 2;
    *(ushort *)(iVar1 + -8) = (ushort)param_1 & 0xff;
    WsfTimerStartMs(iVar1 + -0x10,0x1e);
    uVar2 = param_1;
  }
  return CONCAT44(param_2,uVar2);
}

