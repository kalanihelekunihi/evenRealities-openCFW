
undefined4 DRV_Bq25180SetSystemVoltage(undefined1 param_1)

{
  undefined4 unaff_r7;
  
  bq25180_update_field(10,5,7,param_1);
  return unaff_r7;
}

