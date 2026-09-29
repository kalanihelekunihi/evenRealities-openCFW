
undefined4 semantic_TouchLogCurrentVersion(void)

{
  undefined4 uVar1;
  uint local_c;
  
  local_c = 0;
  FUN_0055b64a();
  FUN_0055b6dc(&local_c);
  uVar1 = DAT_00561760;
  FUN_0044b728(DAT_00561760,0x20,DAT_00561740,local_c >> 0x18,(local_c & 0xffffff) >> 0x10,
               (local_c & 0xffff) >> 8,local_c & 0xff);
  return uVar1;
}

