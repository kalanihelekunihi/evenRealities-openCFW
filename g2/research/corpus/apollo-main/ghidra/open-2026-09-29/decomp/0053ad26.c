
undefined4 DRV_Bq25180SetVdppmEnabled(char param_1)

{
  undefined4 unaff_r7;
  
  bq25180_update_field(10,0,1,param_1 == '\0');
  return unaff_r7;
}

