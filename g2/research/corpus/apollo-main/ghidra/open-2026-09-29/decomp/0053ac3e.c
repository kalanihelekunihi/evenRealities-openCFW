
undefined4 DRV_Bq25180SetPrechargeRatio(byte param_1)

{
  undefined4 unaff_r7;
  
  bq25180_update_field(5,6,1,param_1 < 2);
  return unaff_r7;
}

