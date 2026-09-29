
undefined8 FUN_00505888(int param_1,undefined4 param_2,ushort *param_3,undefined4 param_4)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = FUN_0050633a(param_1,param_3);
  uVar2 = FUN_00508e5c(param_1,0x14,(uint)*(byte *)(param_1 + 0x10) * (uint)*param_3,param_2);
  return CONCAT44(param_4,uVar1 | uVar2);
}

