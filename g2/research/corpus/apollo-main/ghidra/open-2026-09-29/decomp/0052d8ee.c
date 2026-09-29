
undefined1
AttsCsfGetChangeAwareState(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  int iVar2;
  
  if (param_1 == 0) {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0052da20,&DAT_0052da0c,3), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0052da20,DAT_0052da20,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0052da20,DAT_0052da30,4), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if (iVar2 == 0) {
            iVar2 = FUN_004c9c50();
            if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_0052da10,&DAT_0052da14,3), iVar2 != 0)) {
              WsfTrace(DAT_0052da20,DAT_0052da50,0);
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(4,&DAT_0052da10,DAT_0052da2c,DAT_0052da54,0x1bc,DAT_0052da50,0);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(3,&DAT_0052da10,DAT_0052da2c,DAT_0052da54,0x1bc,DAT_0052da50,0);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(2,&DAT_0052da10,DAT_0052da2c,DAT_0052da54,0x1bc,DAT_0052da50,0);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,&DAT_0052da10,DAT_0052da2c,DAT_0052da54,0x1bc,DAT_0052da50,0,param_4);
      }
    }
    uVar1 = 3;
  }
  else {
    uVar1 = *(undefined1 *)(DAT_0052da1c + (uint)param_1 * 2 + -1);
  }
  return uVar1;
}

