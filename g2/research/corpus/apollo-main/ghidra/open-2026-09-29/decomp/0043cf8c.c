
void svc_compress_log_force_sync_to_files(void)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  byte bVar5;
  
  bVar5 = 0;
  iVar2 = FUN_0043d0ce(0);
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_0043d0f8,DAT_0043d0f4,PTR_s_svc_compress_log_force_sync_to_f_0043d124,0x1f2,
                 PTR_s_svc_compress_log_force_sync_to_f_0043d120);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,PTR_s__S200_svc_compress_log_force_syn_0043d128,
                        PTR_s__S200_svc_compress_log_force_syn_0043d128);
  }
  do {
    uVar1 = DAT_0043d110;
    iVar2 = compress_log_ring_read_locked(DAT_0043d110,0x1000);
    if (iVar2 == 0) goto LAB_0043d03a;
    bVar5 = bVar5 + 1;
    compress_log_sync_to_files(uVar1,0x1000);
  } while (bVar5 < 9);
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_0043d0f8,DAT_0043d0f4,PTR_s_svc_compress_log_force_sync_to_f_0043d124,0x1f8,
                 PTR_s_svc_compress_log_force_sync_to_f_0043d12c,bVar5);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__S200_svc_compress_log_force_syn_0043d130,
                        PTR_s__S200_svc_compress_log_force_syn_0043d130,bVar5);
  }
LAB_0043d03a:
  iVar2 = (uint)bVar5 * 0x1000;
  uVar3 = *(uint *)(DAT_0043d0e8 + 8);
  if (*(uint *)(DAT_0043d0e8 + 0xc) < uVar3) {
    iVar4 = *(int *)(DAT_0043d0e8 + 4) - uVar3;
  }
  else {
    iVar4 = -uVar3;
  }
  uVar3 = *(uint *)(DAT_0043d0e8 + 0xc) + iVar4;
  if ((uVar3 != 0) && (iVar4 = _log_get_all_buffer(uVar1,uVar3 & 0xffff), iVar4 != 0)) {
    compress_log_sync_to_files(uVar1,uVar3 & 0xffff);
    iVar2 = iVar2 + (uVar3 & 0xffff);
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(3,DAT_0043d0f8,DAT_0043d0f4,PTR_s_svc_compress_log_force_sync_to_f_0043d124,0x20c,
                 PTR_s_svc_compress_log_force_sync__don_0043d134,bVar5,uVar3,iVar2);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0xcc00000,PTR_s__S200_svc_compress_log_force_syn_0043d138,
                        PTR_s__S200_svc_compress_log_force_syn_0043d138,bVar5,uVar3,iVar2);
  }
  return;
}

