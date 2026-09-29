
undefined4
bq25180_configure_event_mask(int param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  if (param_1 << 0x1f < 0) {
    bq25180_update_field(6,2,1,param_2 == '\0');
  }
  if (param_1 << 0x1e < 0) {
    bq25180_update_field(6,1,1,param_2 == '\0');
  }
  if (param_1 << 0x1d < 0) {
    bq25180_update_field(6,0,1,param_2 == '\0');
  }
  if (param_1 << 0x1c < 0) {
    bq25180_update_field(0xc,7,1,param_2 == '\0');
  }
  if (param_1 << 0x1b < 0) {
    bq25180_update_field(0xc,6,1,param_2 == '\0');
  }
  if (param_1 << 0x1a < 0) {
    bq25180_update_field(0xc,5,1,param_2 == '\0');
  }
  if (param_1 << 0x19 < 0) {
    bq25180_update_field(0xc,4,1,param_2 == '\0');
  }
  return param_4;
}

