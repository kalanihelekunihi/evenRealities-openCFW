
undefined8 FUN_005d018a(undefined4 *param_1,char *param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  undefined4 uVar2;
  char *local_18;
  undefined4 uStack_14;
  
  pcVar1 = (char *)*param_1;
  local_18 = pcVar1;
  uStack_14 = param_4;
  uVar2 = FUN_005d008e(&local_18,param_2,10);
  if (local_18 == pcVar1) {
    uVar2 = 0;
  }
  else {
    if ((local_18 < param_2) && (*local_18 == '#')) {
      pcVar1 = local_18 + 1;
      local_18 = pcVar1;
      uVar2 = FUN_005d008e(&local_18,param_2);
      if (local_18 == pcVar1) {
        uVar2 = 0;
        goto LAB_005d01dc;
      }
    }
    *param_1 = local_18;
  }
LAB_005d01dc:
  return CONCAT44(local_18,uVar2);
}

