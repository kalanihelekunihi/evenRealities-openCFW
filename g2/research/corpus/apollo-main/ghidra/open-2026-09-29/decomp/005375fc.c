
int smpCcbByConnId(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (param_1 == 0) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_00537ea0,&DAT_00537864,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_00537ea0,PTR_DAT_00537ea0,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_00537ea0,DAT_00537eb0,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&LAB_00537868,&LAB_005379f0,3), iVar1 != 0)) {
              WsfTrace(PTR_DAT_00537ea0,DAT_00537ec4,0);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(4,&LAB_00537868,DAT_00537eac,PTR_s_smpCcbByConnId_00537ec8,0x133,
                           DAT_00537ec4,0);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(3,&LAB_00537868,DAT_00537eac,PTR_s_smpCcbByConnId_00537ec8,0x133,
                         DAT_00537ec4,0);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(2,&LAB_00537868,DAT_00537eac,PTR_s_smpCcbByConnId_00537ec8,0x133,DAT_00537ec4
                       ,0);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,&LAB_00537868,DAT_00537eac,PTR_s_smpCcbByConnId_00537ec8,0x133,DAT_00537ec4,0
                     ,param_4);
      }
    }
    iVar1 = 0;
  }
  else {
    iVar1 = DAT_00537ebc + (uint)param_1 * 0x4c + -0x4c;
  }
  return iVar1;
}

