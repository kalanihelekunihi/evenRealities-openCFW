
void AttsCsfSetClientsChangeAwarenessState
               (byte param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  
  if (param_1 == 0) {
    for (bVar1 = 0; bVar1 < 3; bVar1 = bVar1 + 1) {
      if (*(char *)(DAT_0052da1c + (uint)bVar1 * 2 + 1) == '\x02') {
        *(undefined1 *)(DAT_0052da1c + (uint)bVar1 * 2 + 1) = 1;
      }
      else {
        *(undefined1 *)(DAT_0052da1c + (uint)bVar1 * 2 + 1) = param_2;
      }
    }
  }
  else if (param_1 == 0) {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0052da20,&DAT_0052d360,3), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0052da20,DAT_0052da20,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0052da20,DAT_0052da30,4), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if (iVar2 == 0) {
            iVar2 = FUN_004c9c50();
            if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_0052d364,&DAT_0052d36c,3), iVar2 != 0)) {
              WsfTrace(DAT_0052da20,DAT_0052da24,0,param_2);
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(4,&DAT_0052d364,DAT_0052da2c,DAT_0052da28,0x11e,DAT_0052da24,0,param_2);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(3,&DAT_0052d364,DAT_0052da2c,DAT_0052da28,0x11e,DAT_0052da24,0,param_2);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(2,&DAT_0052d364,DAT_0052da2c,DAT_0052da28,0x11e,DAT_0052da24,0,param_2);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,&DAT_0052d364,DAT_0052da2c,DAT_0052da28,0x11e,DAT_0052da24,0,param_2,param_4)
        ;
      }
    }
  }
  else {
    *(undefined1 *)(DAT_0052da1c + (uint)param_1 * 2 + -1) = param_2;
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0052da30,&DAT_0052d360,3), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0052da30,DAT_0052da20,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0052da30,DAT_0052da30,4), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if (iVar2 == 0) {
            iVar2 = FUN_004c9c50();
            if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_0052d364,&DAT_0052d36c,3), iVar2 != 0)) {
              WsfTrace(DAT_0052da30,DAT_0052d500,param_1,param_2);
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(4,&DAT_0052d364,DAT_0052da2c,DAT_0052da28,0x123,DAT_0052d500,param_1,
                           param_2);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(3,&DAT_0052d364,DAT_0052da2c,DAT_0052da28,0x123,DAT_0052d500,param_1,
                         param_2);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(2,&DAT_0052d364,DAT_0052da2c,DAT_0052da28,0x123,DAT_0052d500,param_1,param_2)
          ;
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,&DAT_0052d364,DAT_0052da2c,DAT_0052da28,0x123,DAT_0052d500,param_1,param_2);
      }
    }
  }
  return;
}

