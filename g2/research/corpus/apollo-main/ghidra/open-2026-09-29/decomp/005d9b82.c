
undefined4 _kvdbUpdataRing(void)

{
  int iVar1;
  char cStack_20;
  undefined1 uStack_1f;
  undefined1 uStack_1e;
  undefined1 uStack_1d;
  undefined1 uStack_1c;
  undefined1 uStack_1b;
  undefined1 uStack_1a;
  undefined1 auStack_19 [15];
  short sStack_a;
  
  iVar1 = SVC_KvdbBlobRead(PTR_s_kvRing_005d9e8c,&cStack_20,0x18);
  if (0 < iVar1) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_kv_ring_005d9e9c,DAT_005d9e98,PTR_s__kvdbUpdataRing_005d9e94,0x2d,
                   PTR_s_version__d__d__005d9e90,cStack_20,1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__kv_ring_version__d__d__005d9ea0,
                          PTR_s__kv_ring_version__d__d__005d9ea0,cStack_20,1);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_kv_ring_005d9e9c,DAT_005d9e98,PTR_s__kvdbUpdataRing_005d9e94,0x2e,
                   PTR_s_crc_0x_x_0x_x__005d9ea4,sStack_a,*(undefined2 *)(DAT_005d9e88 + 0x16));
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__kv_ring_crc_0x_x_0x_x__005d9ea8,
                          PTR_s__kv_ring_crc_0x_x_0x_x__005d9ea8,sStack_a,
                          *(undefined2 *)(DAT_005d9e88 + 0x16));
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_kv_ring_005d9e9c,DAT_005d9e98,PTR_s__kvdbUpdataRing_005d9e94,0x30,
                   DAT_005d9eac,uStack_1a,uStack_1b,uStack_1c,uStack_1d,uStack_1e,uStack_1f);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x11800000,DAT_005d9eb0,DAT_005d9eb0,uStack_1a,uStack_1b,uStack_1c,
                          uStack_1d,uStack_1e,uStack_1f);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_kv_ring_005d9e9c,DAT_005d9e98,PTR_s__kvdbUpdataRing_005d9e94,0x31,
                   DAT_005d9eb4,auStack_19);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_005d9eb8,DAT_005d9eb8,auStack_19);
    }
    if ((sStack_a != *(short *)(DAT_005d9e88 + 0x16)) && (cStack_20 == '\0')) {
      SVC_KvdbWriteRing(DAT_005d9e88 + 1,DAT_005d9e88 + 7);
    }
    return 0;
  }
  SVC_KvdbWriteRing(DAT_005d9e88 + 1,DAT_005d9e88 + 7);
  return 0;
}

