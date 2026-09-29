
int attsCcbByConnId(byte param_1,byte param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (param_1 == 0) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0053544c,&LAB_005351d8,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0053544c,DAT_0053544c,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0053544c,DAT_0053545c,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_00535258,&DAT_00535278,3), iVar1 != 0)) {
              WsfTrace(DAT_0053544c,DAT_00535470,0,param_2);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(4,&DAT_00535258,DAT_00535458,DAT_00535474,0x25c,DAT_00535470,0,param_2);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(3,&DAT_00535258,DAT_00535458,DAT_00535474,0x25c,DAT_00535470,0,param_2);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(2,&DAT_00535258,DAT_00535458,DAT_00535474,0x25c,DAT_00535470,0,param_2);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,&DAT_00535258,DAT_00535458,DAT_00535474,0x25c,DAT_00535470,0,param_2,param_4)
        ;
      }
    }
    iVar1 = 0;
  }
  else {
    iVar1 = DmConnInUse(param_1);
    if (iVar1 == 0) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0053544c,&LAB_005351d8,3), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0053544c,DAT_0053544c,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0053544c,DAT_0053545c,4), iVar1 != 0)) {
            iVar1 = FUN_004c9c50();
            if (iVar1 == 0) {
              iVar1 = FUN_004c9c50();
              if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_00535258,&DAT_00535278,3), iVar1 != 0))
              {
                WsfTrace(DAT_0053544c,DAT_00535478,param_1);
              }
            }
            else {
              iVar1 = FUN_0043d0ce();
              if (iVar1 << 0x1e < 0) {
                FUN_0043d574(4,&DAT_00535258,DAT_00535458,DAT_00535474,0x264,DAT_00535478,param_1);
              }
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(3,&DAT_00535258,DAT_00535458,DAT_00535474,0x264,DAT_00535478,param_1);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(2,&DAT_00535258,DAT_00535458,DAT_00535474,0x264,DAT_00535478,param_1);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,&DAT_00535258,DAT_00535458,DAT_00535474,0x264,DAT_00535478,param_1);
        }
      }
      iVar1 = 0;
    }
    else {
      iVar1 = DAT_00535448 + (uint)param_1 * 0xc0 + (uint)param_2 * 0x40 + -0xc0;
    }
  }
  return iVar1;
}

