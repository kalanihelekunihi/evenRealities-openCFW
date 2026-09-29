
void DRV_Bq25180SetBatteryRegulationVoltage
               (ushort param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  if (0x47e < param_1 - 0xdac) {
    if (*DAT_0053af50 == 0) {
      FUN_0043d574(0,DAT_0053af64,DAT_0053af60,DAT_0053af88,0x106,DAT_0053af5c,DAT_0053af8c,
                   DAT_0053af88,0x106,param_4);
      do {
        FUN_0044b0ae();
      } while( true );
    }
    (*(code *)*DAT_0053af50)(DAT_0053af8c,DAT_0053af88,0x106);
  }
  bq25180_write_register(3,(param_1 - 0xdac) / 10 & 0xff);
  return;
}

