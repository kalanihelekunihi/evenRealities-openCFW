
undefined8 FUN_004ac16c(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined2 local_10;
  undefined2 uStack_e;
  undefined4 local_c;
  
  local_10 = (undefined2)param_3;
  uStack_e = (undefined2)((uint)param_3 >> 0x10);
  local_c = param_4;
  iVar1 = productModeGet();
  if (iVar1 != 1) {
    local_10 = 3;
    uStack_e = 1;
    local_c = CONCAT31((int3)((uint)*(undefined4 *)(DAT_004acb1c + 4) >> 8),param_1);
    device_mgr_fn_004c659a(&local_10);
  }
  return CONCAT44(local_c,CONCAT22(uStack_e,local_10));
}

