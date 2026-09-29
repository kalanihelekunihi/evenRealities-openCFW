
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 device_mgr_fn_004c6638(void)

{
  short *psVar1;
  char *pcVar2;
  ushort *puVar3;
  char *pcVar4;
  undefined4 in_r3;
  
  pcVar4 = (char *)FUN_0050938e(0);
  psVar1 = _DAT_004c6c78;
  *_DAT_004c6c78 = *_DAT_004c6c78 + 1;
  if (*pcVar4 == '\x01') {
    FUN_0051283c();
  }
  if (*psVar1 != 0) {
    *psVar1 = 0;
    device_mgr_fn_004c67dc();
    device_mgr_fn_004c6810();
    device_mgr_fn_004c691c();
    device_mgr_fn_004c674c();
    device_mgr_fn_004c6990();
    FUN_0052f38c();
    device_mgr_fn_004c69f4();
  }
  if ((1 < *_DAT_004c6c7c) && (*_DAT_004c6c80 != '\0')) {
    *_DAT_004c6c7c = 0;
    pcVar2 = _DAT_004c6c84;
    if (*_DAT_004c6c84 == '\0') {
      *_DAT_004c6c84 = '\x01';
    }
    else {
      *_DAT_004c6c84 = '\0';
    }
    device_mgr_fn_004c6a56(*pcVar2);
  }
  if ((0x13 < *_DAT_004c6c88) && (*_DAT_004c6c80 != '\0')) {
    *_DAT_004c6c88 = 0;
    device_mgr_fn_004c6a9e();
    device_mgr_fn_004c6ad8();
  }
  puVar3 = _DAT_004c6c8c;
  if (5 < *_DAT_004c6c8c) {
    *_DAT_004c6c90 = 0;
    *puVar3 = 0;
    if (*pcVar4 == '\x01') {
      FUN_00512a70();
    }
  }
  return in_r3;
}

