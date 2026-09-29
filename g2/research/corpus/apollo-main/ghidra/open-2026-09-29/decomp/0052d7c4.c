
undefined8 AttsCsfGetFeatures(byte param_1,undefined4 param_2,uint param_3)

{
  int iVar1;
  
  if (param_1 == 0) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052da20,&DAT_0052da0c,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052da20,DAT_0052da20,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052da20,DAT_0052da30,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_0052da10,&DAT_0052da14,3), iVar1 != 0)) {
              WsfTrace(DAT_0052da20,DAT_0052da48,0);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              param_2 = 0x1a6;
              param_3 = DAT_0052da48;
              FUN_0043d574(4,&DAT_0052da10,DAT_0052da2c,DAT_0052da4c,0x1a6,DAT_0052da48,0);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            param_2 = 0x1a6;
            param_3 = DAT_0052da48;
            FUN_0043d574(3,&DAT_0052da10,DAT_0052da2c,DAT_0052da4c,0x1a6,DAT_0052da48,0);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          param_2 = 0x1a6;
          param_3 = DAT_0052da48;
          FUN_0043d574(2,&DAT_0052da10,DAT_0052da2c,DAT_0052da4c,0x1a6,DAT_0052da48,0);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        param_2 = 0x1a6;
        param_3 = DAT_0052da48;
        FUN_0043d574(1,&DAT_0052da10,DAT_0052da2c,DAT_0052da4c,0x1a6,DAT_0052da48,0);
      }
    }
  }
  else if ((param_3 & 0xff) < 2) {
    FUN_00439be4(param_2,DAT_0052da1c + (uint)param_1 * 2 + -2,param_3 & 0xff);
  }
  return CONCAT44(param_3,param_2);
}

