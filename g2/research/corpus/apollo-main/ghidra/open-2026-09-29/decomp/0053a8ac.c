
undefined4 DRV_Bq25180ReadStatet(ushort *param_1)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  
  if (param_1 == (ushort *)0x0) {
    if (*DAT_0053af50 == 0) {
      FUN_0043d574(0,DAT_0053af64,DAT_0053af60,DAT_0053af68,0xba,DAT_0053af5c,DAT_0053af58,
                   DAT_0053af68,0xba);
      do {
        FUN_0044b0ae();
      } while( true );
    }
    (*(code *)*DAT_0053af50)(DAT_0053af58,DAT_0053af68,0xba);
  }
  iVar1 = bq25180_read_register(0);
  uVar2 = bq25180_read_register(1);
  if ((iVar1 < 0) || ((int)uVar2 < 0)) {
    uVar3 = 0;
  }
  else {
    FUN_0043c0e4(param_1,2,0);
    *param_1 = *param_1 & 0xfffe | (ushort)iVar1 & 1;
    *param_1 = *param_1 & 0xfffd | (ushort)((iVar1 >> 1 & 1U) << 1);
    *param_1 = *param_1 & 0xfffb | (ushort)((iVar1 >> 2 & 1U) << 2);
    *param_1 = *param_1 & 0xfff7 | (ushort)((iVar1 >> 3 & 1U) << 3);
    *param_1 = *param_1 & 0xffef | (ushort)((iVar1 >> 4 & 1U) << 4);
    *param_1 = *param_1 & 0xff9f | (ushort)((iVar1 >> 5 & 3U) << 5);
    *param_1 = *param_1 & 0xff7f | (ushort)((iVar1 >> 7 & 1U) << 7);
    *param_1 = *param_1 & 0xfeff | (ushort)((uVar2 & 1) << 8);
    *param_1 = *param_1 & 0xfdff | (ushort)(((int)uVar2 >> 1 & 1U) << 9);
    *param_1 = *param_1 & 0xfbff | (ushort)(((int)uVar2 >> 2 & 1U) << 10);
    *param_1 = *param_1 & 0xe7ff | (ushort)(((int)uVar2 >> 3 & 3U) << 0xb);
    *param_1 = *param_1 & 0xdfff | (ushort)(((int)uVar2 >> 6 & 1U) << 0xd);
    *param_1 = *param_1 & 0xbfff | (ushort)(((int)uVar2 >> 7 & 1U) << 0xe);
    *DAT_0053af6c = (*param_1 & 0x7f) >> 5;
    uVar3 = 1;
  }
  return uVar3;
}

