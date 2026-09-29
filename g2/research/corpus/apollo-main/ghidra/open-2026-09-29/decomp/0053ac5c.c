
void DRV_Bq25180SetFastchargeCurrent
               (ushort param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  
  if (0x3e3 < param_1 - 5) {
    if (*DAT_0053af50 == 0) {
      FUN_0043d574(0,DAT_0053af64,DAT_0053af60,DAT_0053af98,0x143,DAT_0053af5c,DAT_0053af9c,
                   DAT_0053af98,0x143,param_4);
      do {
        FUN_0044b0ae();
      } while( true );
    }
    (*(code *)*DAT_0053af50)(DAT_0053af9c,DAT_0053af98,0x143);
  }
  cVar1 = (char)param_1 + -5;
  if (0x23 < param_1) {
    if ((param_1 / 10 + 0x1b & 0xff) < 0x80) {
      cVar1 = (char)(param_1 / 10) + '\x1b';
    }
    else {
      cVar1 = '\x7f';
    }
  }
  bq25180_update_field(4,0,0x7f,cVar1);
  return;
}

