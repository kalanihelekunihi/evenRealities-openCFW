
undefined4 DRV_Bq25180RefreshStatus(void)

{
  int *piVar1;
  
  piVar1 = DAT_0053afa0;
  DRV_Bq25180ReadEvent(*DAT_0053afa0 + 0x14);
  DRV_Bq25180ReadStatet(*piVar1 + 0x16);
  return 0;
}

