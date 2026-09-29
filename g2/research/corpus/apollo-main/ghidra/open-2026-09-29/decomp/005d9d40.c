
void SVC_KvdbWriteRing(int param_1,int param_2)

{
  undefined1 *puVar1;
  undefined2 uVar2;
  int iVar3;
  
  if (param_1 == 0) {
    FUN_0043c0e4(DAT_005d9ebc,6,0xff);
  }
  else {
    FUN_00439be4(DAT_005d9ebc,param_1,6);
  }
  puVar1 = DAT_005d9e88;
  if (param_2 == 0) {
    FUN_0043c0e4(DAT_005d9ec0,0xe,0xff);
  }
  else {
    FUN_0044b5a0(DAT_005d9e88 + 7,param_2,0xe);
    puVar1[0x14] = 0;
  }
  puVar1 = DAT_005d9e88;
  *DAT_005d9e88 = 1;
  uVar2 = FUN_0049acd4(puVar1,0x16,0);
  *(undefined2 *)(puVar1 + 0x16) = uVar2;
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_kv_ring_005d9e9c,DAT_005d9e98,DAT_005d9ec8,0x4b,DAT_005d9ec4,
                 *(undefined2 *)(puVar1 + 0x16));
  }
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1f < 0) {
LAB_005d9dc8:
    compress_log_output(0x10400000,DAT_005d9ecc,DAT_005d9ecc,*(undefined2 *)(puVar1 + 0x16));
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1d < 0) goto LAB_005d9dc8;
  }
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_kv_ring_005d9e9c,DAT_005d9e98,DAT_005d9ec8,0x4d,DAT_005d9eac,puVar1[6],
                 puVar1[5],puVar1[4],puVar1[3],puVar1[2],puVar1[1]);
  }
  iVar3 = FUN_0043d0ce();
  if (-1 < iVar3 << 0x1f) {
    iVar3 = FUN_0043d0ce();
    if (-1 < iVar3 << 0x1d) goto LAB_005d9e3c;
  }
  compress_log_output(0x11800000,DAT_005d9eb0,DAT_005d9eb0,puVar1[6],puVar1[5],puVar1[4],puVar1[3],
                      puVar1[2],puVar1[1]);
LAB_005d9e3c:
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_kv_ring_005d9e9c,DAT_005d9e98,DAT_005d9ec8,0x4e,DAT_005d9eb4,puVar1 + 7);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_005d9eb8,DAT_005d9eb8,puVar1 + 7);
  }
  SVC_KvdbBlobWrite(PTR_s_kvRing_005d9e8c,puVar1,0x18);
  return;
}

