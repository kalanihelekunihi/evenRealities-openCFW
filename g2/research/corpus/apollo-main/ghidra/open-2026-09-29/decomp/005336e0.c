
undefined8 FUN_005336e0(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = param_1;
  if ((param_1 & 0xff) == 0) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00533890,&DAT_00533848,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00533890,DAT_00533890,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00533890,DAT_0053389c,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_0053385c,&DAT_00533860,3), iVar1 != 0)) {
              WsfTrace(DAT_00533890,DAT_005338a0,param_1 & 0xff);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              uVar2 = 0x46a;
              param_2 = DAT_005338a0;
              FUN_0043d574(4,&DAT_0053385c,DAT_00533878,DAT_005338a4,0x46a,DAT_005338a0,
                           param_1 & 0xff);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            uVar2 = 0x46a;
            param_2 = DAT_005338a0;
            FUN_0043d574(3,&DAT_0053385c,DAT_00533878,DAT_005338a4,0x46a,DAT_005338a0,param_1 & 0xff
                        );
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          uVar2 = 0x46a;
          param_2 = DAT_005338a0;
          FUN_0043d574(2,&DAT_0053385c,DAT_00533878,DAT_005338a4,0x46a,DAT_005338a0,param_1 & 0xff);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar2 = 0x46a;
        param_2 = DAT_005338a0;
        FUN_0043d574(1,&DAT_0053385c,DAT_00533878,DAT_005338a4,0x46a,DAT_005338a0,param_1 & 0xff);
      }
    }
  }
  else {
    iVar1 = DAT_0053386c + (param_1 & 0xff) * 0x10;
    if (*(char *)(iVar1 + -5) == '\0') {
      *(undefined1 *)(iVar1 + -5) = 3;
      param_2 = 0;
      uVar2 = DAT_005338a8;
      AttcReadByTypeReq(param_1 & 0xff,1,0xffff,2,DAT_005338a8,0,param_3,param_4);
    }
  }
  return CONCAT44(param_2,uVar2);
}

