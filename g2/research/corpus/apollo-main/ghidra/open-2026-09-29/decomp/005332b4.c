
undefined8
FUN_005332b4(uint param_1,uint param_2,undefined4 param_3,undefined4 param_4,undefined4 param_5,
            undefined4 param_6)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  uint uVar4;
  uint uVar5;
  
  uVar4 = param_1;
  if ((param_1 & 0xff) == 0) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00533464,&DAT_00533458,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00533464,DAT_00533464,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00533464,DAT_00533470,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) ||
               (iVar1 = FUN_0044b610(&DAT_00533460,&DAT_00533628,3), uVar5 = param_2, iVar1 != 0)) {
              WsfTrace(DAT_00533464,DAT_00533888,param_1 & 0xff);
              uVar5 = param_2;
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            uVar5 = param_2;
            if (iVar1 << 0x1e < 0) {
              uVar4 = 0x3c9;
              uVar5 = DAT_00533888;
              FUN_0043d574(4,&DAT_00533460,DAT_00533878,DAT_0053388c,0x3c9,DAT_00533888,
                           param_1 & 0xff);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          uVar5 = param_2;
          if (iVar1 << 0x1e < 0) {
            uVar4 = 0x3c9;
            uVar5 = DAT_00533888;
            FUN_0043d574(3,&DAT_00533460,DAT_00533878,DAT_0053388c,0x3c9,DAT_00533888,param_1 & 0xff
                        );
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        uVar5 = param_2;
        if (iVar1 << 0x1e < 0) {
          uVar4 = 0x3c9;
          uVar5 = DAT_00533888;
          FUN_0043d574(2,&DAT_00533460,DAT_00533878,DAT_0053388c,0x3c9,DAT_00533888,param_1 & 0xff);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      uVar5 = param_2;
      if (iVar1 << 0x1e < 0) {
        uVar4 = 0x3c9;
        uVar5 = DAT_00533888;
        FUN_0043d574(1,&DAT_00533460,DAT_00533878,DAT_0053388c,0x3c9,DAT_00533888,param_1 & 0xff,
                     param_4);
      }
    }
  }
  else {
    iVar1 = DAT_0053386c + (param_1 & 0xff) * 0x10;
    piVar3 = (int *)(iVar1 + -0x10);
    uVar5 = param_2;
    if (*piVar3 == 0) {
      iVar2 = WsfBufAlloc(0x14);
      *piVar3 = iVar2;
    }
    if (*piVar3 != 0) {
      DmConnSetIdle(param_1 & 0xff,8,1);
      *(undefined1 *)(iVar1 + -5) = 1;
      *(undefined4 *)*piVar3 = param_5;
      *(undefined4 *)(*piVar3 + 4) = param_6;
      *(char *)(*piVar3 + 0xc) = (char)param_4;
      AttcDiscService(param_1 & 0xff,*piVar3,param_2 & 0xff,param_3);
    }
  }
  return CONCAT44(uVar5,uVar4);
}

