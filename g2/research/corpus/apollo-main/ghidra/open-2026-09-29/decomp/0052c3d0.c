
undefined8 AttsCccClearTable(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = param_1;
  iVar1 = FUN_004c9c50();
  if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052c688,&DAT_0052c660,3), iVar1 != 0)) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052c688,DAT_0052c678,4), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052c688,DAT_0052c688,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if (iVar1 == 0) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_0052c66c,&DAT_0052c670,3), iVar1 != 0)) {
            WsfTrace(DAT_0052c688,DAT_0052c6b4,param_1 & 0xff);
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            uVar2 = 0x188;
            param_2 = DAT_0052c6b4;
            FUN_0043d574(4,&DAT_0052c66c,DAT_0052c684,DAT_0052c6b8,0x188,DAT_0052c6b4,param_1 & 0xff
                        );
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          uVar2 = 0x188;
          param_2 = DAT_0052c6b4;
          FUN_0043d574(3,&DAT_0052c66c,DAT_0052c684,DAT_0052c6b8,0x188,DAT_0052c6b4,param_1 & 0xff);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar2 = 0x188;
        param_2 = DAT_0052c6b4;
        FUN_0043d574(2,&DAT_0052c66c,DAT_0052c684,DAT_0052c6b8,0x188,DAT_0052c6b4,param_1 & 0xff);
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar2 = 0x188;
      param_2 = DAT_0052c6b4;
      FUN_0043d574(1,&DAT_0052c66c,DAT_0052c684,DAT_0052c6b8,0x188,DAT_0052c6b4,param_1 & 0xff,
                   param_4);
    }
  }
  if (((param_1 & 0xff) == 0) || (3 < (param_1 & 0xff))) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052c678,&DAT_0052c660,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052c678,DAT_0052c678,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052c678,DAT_0052c688,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_0052c66c,&DAT_0052c670,3), iVar1 != 0)) {
              WsfTrace(DAT_0052c678,DAT_0052c6bc,param_1 & 0xff);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              uVar2 = 0x18d;
              param_2 = DAT_0052c6bc;
              FUN_0043d574(4,&DAT_0052c66c,DAT_0052c684,DAT_0052c6b8,0x18d,DAT_0052c6bc,
                           param_1 & 0xff);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            uVar2 = 0x18d;
            param_2 = DAT_0052c6bc;
            FUN_0043d574(3,&DAT_0052c66c,DAT_0052c684,DAT_0052c6b8,0x18d,DAT_0052c6bc,param_1 & 0xff
                        );
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          uVar2 = 0x18d;
          param_2 = DAT_0052c6bc;
          FUN_0043d574(2,&DAT_0052c66c,DAT_0052c684,DAT_0052c6b8,0x18d,DAT_0052c6bc,param_1 & 0xff);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar2 = 0x18d;
        param_2 = DAT_0052c6bc;
        FUN_0043d574(1,&DAT_0052c66c,DAT_0052c684,DAT_0052c6b8,0x18d,DAT_0052c6bc,param_1 & 0xff);
      }
    }
  }
  else {
    attsCccFreeTbl(param_1 & 0xff);
  }
  return CONCAT44(param_2,uVar2);
}

