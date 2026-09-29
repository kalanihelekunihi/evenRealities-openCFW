
int attcCcbByConnId(byte param_1,byte param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (param_1 == 0) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00531b90,&DAT_00531ab0,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00531b90,DAT_00531b90,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00531b90,DAT_00531b18,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_00531b94,&DAT_00531b98,3), iVar1 != 0)) {
              WsfTrace(DAT_00531b90,DAT_00531bc0,0,param_2);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(4,&DAT_00531b94,DAT_00531abc,DAT_00531bc4,0x2f0,DAT_00531bc0,0,param_2);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(3,&DAT_005318f8,DAT_00531abc,DAT_00531bc4,0x2f0,DAT_00531bc0,0,param_2);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(2,&DAT_005318f8,DAT_00531abc,DAT_00531bc4,0x2f0,DAT_00531bc0,0,param_2);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,&DAT_005318f8,DAT_00531abc,DAT_00531bc4,0x2f0,DAT_00531bc0,0,param_2,param_4)
        ;
      }
    }
    iVar1 = 0;
  }
  else {
    iVar1 = DmConnInUse(param_1);
    if (iVar1 == 0) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00531b90,&DAT_00531ab0,3), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00531b90,DAT_00531b90,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00531b90,DAT_00531b18,4), iVar1 != 0)) {
            iVar1 = FUN_004c9c50();
            if (iVar1 == 0) {
              iVar1 = FUN_004c9c50();
              if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_00531b94,&DAT_00531b98,3), iVar1 != 0))
              {
                WsfTrace(DAT_00531b90,DAT_00531bc8,param_1);
              }
            }
            else {
              iVar1 = FUN_0043d0ce();
              if (iVar1 << 0x1e < 0) {
                FUN_0043d574(4,&DAT_00531b94,DAT_00531abc,DAT_00531bc4,0x2f9,DAT_00531bc8,param_1);
              }
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(3,&DAT_00531b94,DAT_00531abc,DAT_00531bc4,0x2f9,DAT_00531bc8,param_1);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(2,&DAT_00531b94,DAT_00531abc,DAT_00531bc4,0x2f9,DAT_00531bc8,param_1);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,&DAT_00531b94,DAT_00531abc,DAT_00531bc4,0x2f9,DAT_00531bc8,param_1);
        }
      }
      iVar1 = 0;
    }
    else {
      iVar1 = DAT_00531bac + (uint)param_1 * 0x84 + (uint)param_2 * 0x2c + -0x84;
    }
  }
  return iVar1;
}

