
int DmConnPeerRpa(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (param_1 == 0) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004b7454,&DAT_004b71c4,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004b7454,DAT_004b7454,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004b7454,DAT_004b7464,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_004b71c8,&DAT_004b71cc,3), iVar1 != 0)) {
              WsfTrace(DAT_004b7454,DAT_004b7458,0);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(4,&DAT_004b71c8,DAT_004b7460,DAT_004b745c,0x691,DAT_004b7458,0);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(3,&DAT_004b71c8,DAT_004b7460,DAT_004b745c,0x691,DAT_004b7458,0);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(2,&DAT_004b71c8,DAT_004b7460,DAT_004b745c,0x691,DAT_004b7458,0);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,&DAT_004b71c8,DAT_004b7460,DAT_004b745c,0x691,DAT_004b7458,0,param_4);
      }
    }
    iVar1 = 0;
  }
  else {
    iVar1 = DAT_004b7430 + (uint)param_1 * 0x30 + -0x10;
  }
  return iVar1;
}

