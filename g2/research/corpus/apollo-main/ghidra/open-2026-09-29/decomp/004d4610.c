
undefined8
FUN_004d4610(undefined4 *param_1,undefined4 param_2,uint param_3,undefined4 param_4,uint param_5,
            undefined4 param_6)

{
  int iVar1;
  
  param_1[1] = param_6;
  *param_1 = param_4;
  param_3 = param_3 & 0xff;
  iVar1 = FUN_004548ba(0x4d4769,param_2,param_5 >> 2 & 0xffff,param_1,param_3,param_1 + 2,param_4);
  if (iVar1 != 1) {
    param_3 = DAT_004d47a8;
    FUN_0044d25c(3,DAT_004d47b0,0x67,DAT_004d47ac);
  }
  return CONCAT44(param_3,(uint)(iVar1 == 1));
}

