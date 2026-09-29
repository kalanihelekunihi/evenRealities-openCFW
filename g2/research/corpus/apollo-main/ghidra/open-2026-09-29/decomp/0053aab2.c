
undefined4 DRV_Bq25180SetSafetyTimer(undefined1 param_1)

{
  undefined4 unaff_r7;
  
  bq25180_update_field(7,2,3,param_1);
  return unaff_r7;
}

