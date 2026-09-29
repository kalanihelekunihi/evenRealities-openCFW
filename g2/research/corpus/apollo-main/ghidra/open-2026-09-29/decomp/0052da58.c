
int attsSignCcbByConnId(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (param_1 == 0) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052dba0,&DAT_0052db94,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052dba0,DAT_0052dba0,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052dba0,DAT_0052dbb0,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_0052db98,&DAT_0052db9c,3), iVar1 != 0)) {
              WsfTrace(DAT_0052dba0,DAT_0052dba4,0);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(4,&DAT_0052db98,DAT_0052dbac,DAT_0052dba8,0x5d,DAT_0052dba4,0);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(3,&DAT_0052db98,DAT_0052dbac,DAT_0052dba8,0x5d,DAT_0052dba4,0);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(2,&DAT_0052db98,DAT_0052dbac,DAT_0052dba8,0x5d,DAT_0052dba4,0);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,&DAT_0052db98,DAT_0052dbac,DAT_0052dba8,0x5d,DAT_0052dba4,0,param_4);
      }
    }
    iVar1 = 0;
  }
  else {
    iVar1 = DAT_0052dbb4 + (uint)param_1 * 0x10 + -0x10;
  }
  return iVar1;
}

