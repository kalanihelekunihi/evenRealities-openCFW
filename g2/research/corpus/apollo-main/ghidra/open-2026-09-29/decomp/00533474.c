
undefined8
FUN_00533474(uint param_1,uint param_2,undefined1 param_3,undefined4 param_4,undefined1 param_5,
            undefined4 param_6)

{
  char cVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  uint uVar5;
  uint uVar6;
  
  uVar5 = param_1;
  if ((param_1 & 0xff) == 0) {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_00533890,&DAT_005336c0,3), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_00533890,DAT_00533890,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_00533890,DAT_0053389c,4), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if (iVar2 == 0) {
            iVar2 = FUN_004c9c50();
            if ((iVar2 == 0) ||
               (iVar2 = FUN_0044b610(&DAT_005336c4,&DAT_00533628,3), uVar6 = param_2, iVar2 != 0)) {
              WsfTrace(DAT_00533890,DAT_00533894,param_1 & 0xff);
              uVar6 = param_2;
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            uVar6 = param_2;
            if (iVar2 << 0x1e < 0) {
              uVar5 = 0x3f4;
              uVar6 = DAT_00533894;
              FUN_0043d574(4,&DAT_005336c4,DAT_00533878,DAT_00533898,0x3f4,DAT_00533894,
                           param_1 & 0xff);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          uVar6 = param_2;
          if (iVar2 << 0x1e < 0) {
            uVar5 = 0x3f4;
            uVar6 = DAT_00533894;
            FUN_0043d574(3,&DAT_005336c4,DAT_00533878,DAT_00533898,0x3f4,DAT_00533894,param_1 & 0xff
                        );
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        uVar6 = param_2;
        if (iVar2 << 0x1e < 0) {
          uVar5 = 0x3f4;
          uVar6 = DAT_00533894;
          FUN_0043d574(2,&DAT_005336c4,DAT_00533878,DAT_00533898,0x3f4,DAT_00533894,param_1 & 0xff);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      uVar6 = param_2;
      if (iVar2 << 0x1e < 0) {
        uVar5 = 0x3f4;
        uVar6 = DAT_00533894;
        FUN_0043d574(1,&DAT_005336c4,DAT_00533878,DAT_00533898,0x3f4,DAT_00533894,param_1 & 0xff,
                     param_4);
      }
    }
  }
  else {
    iVar2 = DAT_0053386c + (param_1 & 0xff) * 0x10;
    piVar4 = (int *)(iVar2 + -0x10);
    uVar6 = param_2;
    if (*piVar4 == 0) {
      iVar3 = WsfBufAlloc(0x14);
      *piVar4 = iVar3;
    }
    if (*piVar4 != 0) {
      DmConnSetIdle(param_1 & 0xff,8,1);
      *(undefined1 *)(iVar2 + -5) = 2;
      if ((param_2 & 0xff) == 7) {
        *(undefined1 *)(iVar2 + -8) = 7;
      }
      *(undefined4 *)(*piVar4 + 8) = param_4;
      *(undefined1 *)(*piVar4 + 0xd) = param_3;
      *(undefined4 *)(*piVar4 + 4) = param_6;
      *(undefined1 *)(*piVar4 + 0xc) = param_5;
      cVar1 = AttcDiscConfigStart(param_1 & 0xff,*piVar4);
      if (cVar1 == '\0') {
        (*(code *)*DAT_00533624)(param_1 & 0xff,8);
      }
    }
  }
  return CONCAT44(uVar6,uVar5);
}

