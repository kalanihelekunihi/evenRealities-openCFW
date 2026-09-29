
undefined4 DRV_Bq25180SetPrechargeThreshold(ushort param_1)

{
  undefined4 unaff_r7;
  
  bq25180_update_field(7,6,1,param_1 < 0xaf1);
  return unaff_r7;
}

