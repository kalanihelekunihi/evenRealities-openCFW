
undefined4 semantic_OtaCancelExport(void)

{
  undefined1 *puVar1;
  undefined4 in_r3;
  
  puVar1 = DAT_00448878;
  FUN_0043c0e4(DAT_00448878,0x60,0);
  *puVar1 = 0;
  *(undefined4 *)(puVar1 + 0x34) = DAT_0044887c;
  _RPC_SystemOtaStatusSync(0);
  return in_r3;
}

