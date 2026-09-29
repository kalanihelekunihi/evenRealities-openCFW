
uint bq25180_update_field(undefined1 param_1,uint param_2,uint param_3,uint param_4)

{
  uint uVar1;
  
  uVar1 = bq25180_read_register(param_1);
  bq25180_write_register
            (param_1,((param_4 & 0xff) << (param_2 & 0xff) |
                     uVar1 & ~((param_3 & 0xff) << (param_2 & 0xff))) & 0xff);
  return param_4;
}

