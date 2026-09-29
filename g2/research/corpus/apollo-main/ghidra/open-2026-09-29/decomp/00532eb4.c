
undefined8 FUN_00532eb4(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = param_1;
  if ((param_1 & 0xff) == 0) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00533464,&DAT_00532ffc,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00533464,DAT_00533464,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00533464,DAT_00533470,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_00533004,&DAT_00533020,3), iVar1 != 0)) {
              WsfTrace(DAT_00533464,DAT_00533864,param_1 & 0xff);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              uVar2 = 0x368;
              param_2 = DAT_00533864;
              FUN_0043d574(4,&DAT_00533004,DAT_0053302c,DAT_00533868,0x368,DAT_00533864,
                           param_1 & 0xff);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            uVar2 = 0x368;
            param_2 = DAT_00533864;
            FUN_0043d574(3,&DAT_00533004,DAT_0053302c,DAT_00533868,0x368,DAT_00533864,param_1 & 0xff
                        );
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          uVar2 = 0x368;
          param_2 = DAT_00533864;
          FUN_0043d574(2,&DAT_00533004,DAT_0053302c,DAT_00533868,0x368,DAT_00533864,param_1 & 0xff);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar2 = 0x368;
        param_2 = DAT_00533864;
        FUN_0043d574(1,&DAT_00533004,DAT_0053302c,DAT_00533868,0x368,DAT_00533864,param_1 & 0xff,
                     param_4);
      }
    }
  }
  else {
    iVar1 = DAT_0053386c + (param_1 & 0xff) * 0x10;
    *(char *)(iVar1 + -6) = (char)param_2;
    *(undefined4 *)(iVar1 + -0xc) = param_3;
  }
  return CONCAT44(param_2,uVar2);
}

