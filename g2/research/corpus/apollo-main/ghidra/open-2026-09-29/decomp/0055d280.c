
undefined8 FUN_0055d280(undefined4 param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  uint uVar1;
  uint uVar2;
  uint local_10;
  
  local_10 = param_4;
  uVar1 = FUN_00508e5c(param_1,0x30,1,&local_10);
  local_10 = local_10 & 0xfffffff3 | 0x14;
  uVar2 = FUN_00508e74(param_1,0x30,1,&local_10);
  return CONCAT44(local_10,uVar1 | uVar2);
}

