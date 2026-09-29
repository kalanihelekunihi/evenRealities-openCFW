
undefined8 FUN_004505a2(uint param_1,uint param_2,uint param_3,undefined4 param_4)

{
  uint uVar1;
  
  uVar1 = param_2;
  if (10000 < param_1) {
    uVar1 = DAT_00450b4c;
    FUN_0044d25c(2,DAT_00450b44,0xd8,DAT_00450b50,DAT_00450b4c,param_1,param_4);
    param_1 = 0x27f6;
  }
  if (10000 < param_2) {
    uVar1 = DAT_00450b54;
    FUN_0044d25c(2,DAT_00450b44,0xdc,DAT_00450b50,DAT_00450b54,param_2,param_4);
    param_2 = 0x27f6;
  }
  if (10000 < param_3) {
    uVar1 = DAT_00450b58;
    FUN_0044d25c(2,DAT_00450b44,0xe0,DAT_00450b50,DAT_00450b58,param_3,param_4);
    param_3 = 0x27f6;
  }
  return CONCAT44(uVar1,(param_1 + 5) / 10 +
                        ((param_2 + 5) / 10) * 0x400 + ((param_3 + 5) / 10) * 0x100000 + -0x80000000
                 );
}

