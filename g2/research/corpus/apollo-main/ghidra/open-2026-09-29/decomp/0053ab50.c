
undefined4 DRV_Bq25180SetBatteryOvercurrent(undefined1 param_1)

{
  undefined4 unaff_r7;
  
  bq25180_update_field(6,6,3,param_1);
  return unaff_r7;
}

