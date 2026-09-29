
undefined8 FUN_0055d510(undefined4 param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  uint uVar2;
  undefined4 local_18;
  
  local_18 = param_4;
  uVar1 = FUN_00508e5c(param_1,0xa216,1,&local_18);
  local_18 = CONCAT31(local_18._1_3_,(byte)local_18 & 0xf7 | 1 | (param_2 == '\0') << 3);
  uVar2 = FUN_00508e74(param_1,0xa216,1,&local_18);
  return CONCAT44(local_18,uVar1 | uVar2);
}

