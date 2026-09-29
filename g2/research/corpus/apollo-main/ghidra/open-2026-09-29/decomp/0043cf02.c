
undefined8 svc_compress_log_sync_to_files(undefined4 param_1,undefined4 param_2,undefined *param_3)

{
  undefined4 uVar1;
  uint uVar2;
  int iVar3;
  byte bVar4;
  
  uVar2 = osKernelGetTickCount();
  if (*DAT_0043d10c + 10000 < uVar2) {
    *DAT_0043d10c = uVar2;
    bVar4 = 0;
    do {
      uVar1 = DAT_0043d110;
      iVar3 = compress_log_ring_read_locked(DAT_0043d110,0x1000);
      if (iVar3 == 0) break;
      bVar4 = bVar4 + 1;
      compress_log_sync_to_files(uVar1,0x1000);
    } while (bVar4 < 9);
    if (bVar4 != 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_2 = 0x1e8;
        param_3 = PTR_s__CLOG__svc_compress_log_sync_to__0043d114;
        FUN_0043d574(4,DAT_0043d0f8,DAT_0043d0f4,PTR_s_svc_compress_log_sync_to_files_0043d118,0x1e8
                     ,PTR_s__CLOG__svc_compress_log_sync_to__0043d114,bVar4);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10400000,PTR_s__S200__CLOG__svc_compress_log_sy_0043d11c,
                            PTR_s__S200__CLOG__svc_compress_log_sy_0043d11c,bVar4);
      }
    }
  }
  return CONCAT44(param_3,param_2);
}

