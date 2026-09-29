
undefined8 attsConnCback(int param_1,int param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  byte bVar3;
  int iVar4;
  
  iVar4 = param_2;
  if (*(char *)(param_2 + 2) == '(') {
    for (bVar3 = 0; bVar3 < 3; bVar3 = bVar3 + 1) {
      if (*(char *)(param_1 + 0xe) == '\0') {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0053544c,&DAT_00534dd0,3), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0053544c,DAT_0053544c,4), iVar2 != 0)) {
            iVar2 = FUN_004c9c50();
            if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0053544c,DAT_0053545c,4), iVar2 != 0)) {
              iVar2 = FUN_004c9c50();
              if (iVar2 == 0) {
                iVar2 = FUN_004c9c50();
                if ((iVar2 == 0) ||
                   (iVar2 = FUN_0044b610(&DAT_00534dd4,&DAT_00534f10,3), iVar2 != 0)) {
                  WsfTrace(DAT_0053544c,DAT_00535450,*(undefined1 *)(param_1 + 0xe));
                }
              }
              else {
                iVar2 = FUN_0043d0ce();
                if (iVar2 << 0x1e < 0) {
                  iVar4 = 0x10e;
                  param_3 = DAT_00535450;
                  FUN_0043d574(4,&DAT_00534dd4,DAT_00535458,DAT_00535454,0x10e,DAT_00535450,
                               *(undefined1 *)(param_1 + 0xe));
                }
              }
            }
            else {
              iVar2 = FUN_0043d0ce();
              if (iVar2 << 0x1e < 0) {
                iVar4 = 0x10e;
                param_3 = DAT_00535450;
                FUN_0043d574(3,&DAT_00534dd4,DAT_00535458,DAT_00535454,0x10e,DAT_00535450,
                             *(undefined1 *)(param_1 + 0xe));
              }
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              iVar4 = 0x10e;
              param_3 = DAT_00535450;
              FUN_0043d574(2,&DAT_00534dd4,DAT_00535458,DAT_00535454,0x10e,DAT_00535450,
                           *(undefined1 *)(param_1 + 0xe));
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            iVar4 = 0x10e;
            param_3 = DAT_00535450;
            FUN_0043d574(1,&DAT_00534dd4,DAT_00535458,DAT_00535454,0x10e,DAT_00535450,
                         *(undefined1 *)(param_1 + 0xe));
          }
        }
        goto LAB_00534c40;
      }
      iVar2 = DAT_00535448 + (uint)*(byte *)(param_1 + 0xe) * 0xc0 + (uint)bVar3 * 0x40;
      attsClearPrepWrites(iVar2 + -0xc0);
      iVar1 = DmConnCheckIdle(*(undefined1 *)(param_1 + 0xe));
      if (iVar1 << 0x1d < 0) {
        WsfTimerStop(iVar2 + -0xac);
      }
    }
  }
  (**(code **)(*(int *)(DAT_00535448 + 0x260) + 0xc))(param_1,param_2);
LAB_00534c40:
  return CONCAT44(param_3,iVar4);
}

