
undefined8 FUN_005d0814(undefined4 *param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  byte *local_18;
  undefined4 uStack_14;
  
  local_18 = (byte *)*param_1;
  uVar1 = 0;
  uStack_14 = param_4;
  do {
    local_18 = local_18 + 1;
    if ((param_2 <= local_18) || (FUN_005d0736(&local_18,param_2), param_2 <= local_18)) break;
  } while ((*local_18 - 0x30 < 10) || ((*local_18 - 0x41 < 6 || (*local_18 - 0x61 < 6))));
  if ((local_18 < param_2) && (*local_18 != 0x3e)) {
    uVar1 = 3;
  }
  else {
    local_18 = local_18 + 1;
  }
  *param_1 = local_18;
  return CONCAT44(local_18,uVar1);
}

