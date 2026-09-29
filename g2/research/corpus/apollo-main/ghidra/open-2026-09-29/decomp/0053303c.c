
void FUN_0053303c(byte param_1,byte param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int *piVar5;
  
  if (param_1 == 0) {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_00533464,&DAT_00533284,3), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_00533464,DAT_00533464,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_00533464,DAT_00533470,4), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if (iVar2 == 0) {
            iVar2 = FUN_004c9c50();
            if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_00533288,&DAT_00533294,3), iVar2 != 0)) {
              WsfTrace(DAT_00533464,DAT_00533870,0,param_2);
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(4,&DAT_00533288,DAT_00533878,DAT_00533874,0x37f,DAT_00533870,0,param_2);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(3,&DAT_00533288,DAT_00533878,DAT_00533874,0x37f,DAT_00533870,0,param_2);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(2,&DAT_00533288,DAT_00533878,DAT_00533874,0x37f,DAT_00533870,0,param_2);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,&DAT_00533288,DAT_00533878,DAT_00533874,0x37f,DAT_00533870,0,param_2,param_4)
        ;
      }
    }
  }
  else {
    iVar2 = DAT_0053345c + (uint)param_1 * 0x10;
    piVar5 = (int *)(iVar2 + -0x10);
    DmConnSetIdle(param_1,8,0);
    if ((param_2 != 8) || (*(char *)(iVar2 + -8) != '\a')) {
      *(byte *)(iVar2 + -7) = param_2;
    }
    *(undefined1 *)(iVar2 + -5) = 0;
    if (*piVar5 != 0) {
      WsfBufFree(*piVar5);
      *piVar5 = 0;
    }
    iVar3 = FUN_004bb07c(param_1);
    if (iVar3 != 0) {
      iVar4 = FUN_004bad26(param_1);
      if (iVar4 == 0) {
        bVar1 = 4;
      }
      else {
        bVar1 = 8;
      }
      if (((param_2 != 8) || (*(char *)(iVar2 + -8) != '\a')) && (param_2 <= bVar1)) {
        FUN_0047b488(iVar3,param_2);
      }
      if ((*(int *)(iVar2 + -0xc) != 0) && (param_2 == 4)) {
        FUN_0047b48e(iVar3,*(undefined4 *)(iVar2 + -0xc));
      }
    }
    if (param_2 == 8) {
      *(undefined1 *)(iVar2 + -8) = 8;
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00533880,DAT_00533878,DAT_00533874,0x3b3,DAT_0053387c,param_1,param_2);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_00533884,DAT_00533884,param_1,param_2);
    }
  }
  return;
}

