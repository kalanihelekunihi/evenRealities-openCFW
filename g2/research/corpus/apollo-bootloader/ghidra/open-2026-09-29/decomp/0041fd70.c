
longlong FUN_0041fd70(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  uint uVar2;
  
  uVar1 = DAT_0041fda8;
  FUN_0041560c(DAT_0041fda8,0x70800,0,param_4,param_2,param_3,param_4);
  uVar1 = FUN_00417240(uVar1,0x70800);
  *DAT_0041fdac = uVar1;
  uVar2 = 0x13;
  elog_output(4,DAT_0041fdbc,DAT_0041fdb8,DAT_0041fdb4,0x13,DAT_0041fdb0);
  return (ulonglong)uVar2 << 0x20;
}

