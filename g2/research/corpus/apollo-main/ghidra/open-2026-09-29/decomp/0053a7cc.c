
bool DRV_Bq25180ReadEvent(byte *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  
  if (param_1 == (byte *)0x0) {
    if (*DAT_0053af50 == 0) {
      FUN_0043d574(0,DAT_0053af64,DAT_0053af60,DAT_0053af54,0x9c,DAT_0053af5c,DAT_0053af58,
                   DAT_0053af54,0x9c,param_4);
      do {
        FUN_0044b0ae();
      } while( true );
    }
    (*(code *)*DAT_0053af50)(DAT_0053af58,DAT_0053af54,0x9c);
  }
  uVar1 = bq25180_read_register(2);
  if (-1 < (int)uVar1) {
    FUN_0043c0e4(param_1,1,0);
    *param_1 = *param_1 & 0xfe | (byte)uVar1 & 1;
    *param_1 = *param_1 & 0xfd | (byte)(((uVar1 & 0xff) >> 1 & 1) << 1);
    *param_1 = *param_1 & 0xfb | (byte)(((uVar1 & 0xff) >> 2 & 1) << 2);
    *param_1 = *param_1 & 0xf7 | (byte)(((uVar1 & 0xff) >> 3 & 1) << 3);
    *param_1 = *param_1 & 0xef | (byte)(((uVar1 & 0xff) >> 4 & 1) << 4);
    *param_1 = *param_1 & 0xdf | (byte)(((uVar1 & 0xff) >> 5 & 1) << 5);
    *param_1 = *param_1 & 0xbf | (byte)(((uVar1 & 0xff) >> 6 & 1) << 6);
    *param_1 = (byte)uVar1 & 0x80 | *param_1 & 0x7f;
  }
  return -1 < (int)uVar1;
}

