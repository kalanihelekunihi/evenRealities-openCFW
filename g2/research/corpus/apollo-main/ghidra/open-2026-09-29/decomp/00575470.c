
undefined8 pt_cmd_52_handler(int param_1,uint param_2,int param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint local_20;
  int local_1c;
  uint uStack_18;
  
  local_1c = param_3;
  uStack_18 = param_4;
  iVar1 = FUN_0043d0ce();
  local_20 = param_2;
  if (iVar1 << 0x1e < 0) {
    local_1c = DAT_00575e8c;
    local_20 = 0xbf5;
    FUN_0043d574(3,DAT_00575e98,DAT_00575e94,DAT_00575e90);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_00575e9c,DAT_00575e9c);
  }
  if ((((param_1 == 0) || (param_3 == 0)) || (param_4 == 0)) || ((param_2 & 0xff) < 4)) {
    uVar2 = 0xffffffff;
  }
  else {
    OTA_SetInterface(1);
    *DAT_00575ea0 = 0;
    *DAT_00575ea4 = 1;
    *DAT_005760ec = 0;
    FUN_0043c0e4(&local_1c,1,0);
    semantic_OtaFrameDispatch(0xc0,&local_1c,1);
    uVar2 = osThreadGetId();
    osThreadSetPriority(uVar2,0x2f);
    uVar2 = pt_handler_result(0x52,0,3,param_3);
    local_20 = param_4;
  }
  return CONCAT44(local_20,uVar2);
}

