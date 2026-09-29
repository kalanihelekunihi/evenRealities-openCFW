
undefined8 appSlaveAdvMode(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  
  iVar2 = DAT_004b2dc8;
  if (*(int *)(DAT_004b2dc8 + 0x78) == 0) {
    *(int *)(DAT_004b2dc8 + 0x78) = DAT_004b2ddc;
    *(undefined4 *)(iVar2 + 0x7c) = DAT_004b2de0;
    uVar1 = 1;
  }
  else if (*(int *)(DAT_004b2dc8 + 0x78) == DAT_004b2ddc) {
    uVar1 = 1;
  }
  else {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_004b2de4,&DAT_004b2dbc,3), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_004b2de4,DAT_004b2de4,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_004b2de4,DAT_004b2df4,4), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if (iVar2 == 0) {
            iVar2 = FUN_004c9c50();
            if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_004b2dc0,&DAT_004b2dc4,3), iVar2 != 0)) {
              WsfTrace(DAT_004b2de4,DAT_004b2de8);
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              unaff_r5 = 0x142;
              FUN_0043d574(4,&DAT_004b2dc0,DAT_004b2df0,DAT_004b2dec,0x142,DAT_004b2de8);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            unaff_r5 = 0x142;
            FUN_0043d574(3,&DAT_004b2dc0,DAT_004b2df0,DAT_004b2dec,0x142,DAT_004b2de8);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          unaff_r5 = 0x142;
          FUN_0043d574(2,&DAT_004b2dc0,DAT_004b2df0,DAT_004b2dec,0x142,DAT_004b2de8);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        unaff_r5 = 0x142;
        FUN_0043d574(1,&DAT_004b2dc0,DAT_004b2df0,DAT_004b2dec,0x142,DAT_004b2de8);
      }
    }
    uVar1 = 0;
  }
  return CONCAT44(unaff_r5,uVar1);
}

