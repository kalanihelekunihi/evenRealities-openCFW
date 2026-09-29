
void DRV_Bq25180SetBatteryUnderVoltage_lockout
               (ushort param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  
  if (1000 < param_1 - 2000) {
    if (*DAT_0053af50 == 0) {
      FUN_0043d574(0,DAT_0053af64,DAT_0053af60,DAT_0053af90,0x117,DAT_0053af5c,DAT_0053af94,
                   DAT_0053af90,0x117,param_4);
      do {
        FUN_0044b0ae();
      } while( true );
    }
    (*(code *)*DAT_0053af50)(DAT_0053af94,DAT_0053af90,0x117);
  }
  if (param_1 < 0xaf1) {
    if (param_1 < 0xa29) {
      if (param_1 < 0x961) {
        if (param_1 < 0x899) {
          if (param_1 < 0x7d1) {
            uVar1 = 7;
          }
          else {
            uVar1 = 6;
          }
        }
        else {
          uVar1 = 5;
        }
      }
      else {
        uVar1 = 4;
      }
    }
    else {
      uVar1 = 3;
    }
  }
  else {
    uVar1 = 2;
  }
  bq25180_update_field(6,3,7,uVar1);
  return;
}

