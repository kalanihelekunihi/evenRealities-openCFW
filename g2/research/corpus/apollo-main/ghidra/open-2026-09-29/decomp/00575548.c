
undefined4 pt_cmd_53_handler(int param_1,uint param_2,uint param_3,int param_4)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 *puVar4;
  uint local_2c;
  uint local_28;
  int iStack_24;
  
  local_2c = param_2;
  local_28 = param_3;
  iStack_24 = param_4;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    local_2c = DAT_00575ea8;
    FUN_0043d574(3,DAT_00575e98,DAT_00575e94,DAT_00575eac,0xc0e);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_00575eb0,DAT_00575eb0);
  }
  if ((((param_1 == 0) || (param_3 == 0)) || (param_4 == 0)) || ((param_2 & 0xff) < 0x80)) {
    uVar3 = 0xffffffff;
  }
  else {
    bVar1 = *(byte *)(param_1 + 3);
    if (bVar1 == 0x80) {
      puVar4 = (undefined1 *)file_heap_allocate(0x81);
      if (puVar4 == (undefined1 *)0x0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          local_2c = DAT_005760fc;
          FUN_0043d574(1,DAT_00575e98,DAT_00575e94,DAT_00575eac,0xc1d);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_00576100,DAT_00576100);
        }
        uVar3 = pt_handler_result(0x53,1,3,param_3,param_4);
      }
      else {
        *puVar4 = 1;
        FUN_00439be4(puVar4 + 1,param_1 + 4,0x80);
        semantic_OtaFrameDispatch(0xc0,puVar4,0x81);
        file_heap_free(puVar4);
        local_2c = CONCAT31(local_2c._1_3_,2);
        semantic_OtaFrameDispatch(0xc0,&local_2c,1);
        uVar3 = pt_handler_result(0x53,0,3,param_3,param_4);
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_28 = (uint)bVar1;
        local_2c = DAT_005760f0;
        FUN_0043d574(1,DAT_00575e98,DAT_00575e94,DAT_00575eac,0xc15);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_005760f4,DAT_005760f4,bVar1);
      }
      uVar3 = pt_handler_result(0x53,3,3,param_3,param_4);
    }
  }
  return uVar3;
}

