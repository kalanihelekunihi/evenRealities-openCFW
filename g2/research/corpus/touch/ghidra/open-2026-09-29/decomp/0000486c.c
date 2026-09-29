
undefined4 touch_platform_156c_record_init(undefined4 *param_1)

{
  undefined4 uVar1;
  
  uVar1 = DAT_000048c8;
  if (param_1 != (undefined4 *)0x0) {
    param_1[5] = DAT_000048a4;
    param_1[6] = DAT_000048a8;
    param_1[7] = DAT_000048ac;
    param_1[8] = 0;
    param_1[9] = 0;
    param_1[1] = DAT_000048b0;
    param_1[2] = DAT_000048b4;
    param_1[3] = DAT_000048b8;
    param_1[4] = DAT_000048bc;
    param_1[10] = DAT_000048c0;
    param_1[0xb] = DAT_000048c4;
    *param_1 = 0;
    uVar1 = 0;
  }
  return uVar1;
}

