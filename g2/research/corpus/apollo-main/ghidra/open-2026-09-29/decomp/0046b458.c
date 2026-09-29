
undefined8
SVC_Settings_DumpSettingConfig
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  int iVar2;
  
  puVar1 = DAT_0046bee8;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0xaa;
    param_3 = DAT_0046beec;
    FUN_0043d574(3,DAT_0046bb74,DAT_0046bb70,DAT_0046bf60,0xaa,DAT_0046beec,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_0046b494:
    compress_log_output(0xc000000,DAT_0046bef0,DAT_0046bef0);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_0046b494;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0xab;
    param_3 = DAT_0046bef4;
    FUN_0043d574(3,DAT_0046bb74,DAT_0046bb70,DAT_0046bf60,0xab,DAT_0046bef4,*puVar1);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_0046b4da:
    compress_log_output(0xc400000,DAT_0046bf64,DAT_0046bf64,*puVar1);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_0046b4da;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0xac;
    param_3 = DAT_0046bf68;
    FUN_0043d574(3,DAT_0046bb74,DAT_0046bb70,DAT_0046bf60,0xac,DAT_0046bf68,puVar1[1]);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_0046b522:
    compress_log_output(0xc400000,DAT_0046bf6c,DAT_0046bf6c,puVar1[1]);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_0046b522;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0xad;
    param_3 = DAT_0046bf70;
    FUN_0043d574(3,DAT_0046bb74,DAT_0046bb70,DAT_0046bf60,0xad,DAT_0046bf70,puVar1[2]);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_0046b56a:
    compress_log_output(0xc400000,DAT_0046bff0,DAT_0046bff0,puVar1[2]);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_0046b56a;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0xae;
    param_3 = DAT_0046c004;
    FUN_0043d574(3,DAT_0046bb74,DAT_0046bb70,DAT_0046bf60,0xae,DAT_0046c004,puVar1[8]);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_0046b5b2:
    compress_log_output(0xc400000,DAT_0046c008,DAT_0046c008,puVar1[8]);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_0046b5b2;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0xaf;
    param_3 = DAT_0046c00c;
    FUN_0043d574(3,DAT_0046bb74,DAT_0046bb70,DAT_0046bf60,0xaf,DAT_0046c00c,puVar1[9]);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_0046b5fa:
    compress_log_output(0xc400000,DAT_0046c010,DAT_0046c010,puVar1[9]);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_0046b5fa;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0xb0;
    param_3 = DAT_0046c014;
    FUN_0043d574(3,DAT_0046bb74,DAT_0046bb70,DAT_0046bf60,0xb0,DAT_0046c014,puVar1[10]);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_0046b642:
    compress_log_output(0xc400000,DAT_0046c018,DAT_0046c018,puVar1[10]);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_0046b642;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0xb1;
    param_3 = DAT_0046c0dc;
    FUN_0043d574(3,DAT_0046bb74,DAT_0046bb70,DAT_0046bf60,0xb1,DAT_0046c0dc,
                 *(undefined4 *)(puVar1 + 0xc));
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_0046b68a:
    compress_log_output(0xc400000,DAT_0046c0e0,DAT_0046c0e0,*(undefined4 *)(puVar1 + 0xc));
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_0046b68a;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0xb2;
    param_3 = DAT_0046c0e4;
    FUN_0043d574(3,DAT_0046bb74,DAT_0046bb70,DAT_0046bf60,0xb2,DAT_0046c0e4,puVar1[0x14]);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_0046b6d2:
    compress_log_output(0xc400000,DAT_0046c150,DAT_0046c150,puVar1[0x14]);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_0046b6d2;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0xb3;
    param_3 = DAT_0046c154;
    FUN_0043d574(3,DAT_0046bb74,DAT_0046bb70,DAT_0046bf60,0xb3,DAT_0046c154,puVar1[0x15]);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_0046b71a:
    compress_log_output(0xc400000,DAT_0046c188,DAT_0046c188,puVar1[0x15]);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_0046b71a;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0xb4;
    param_3 = DAT_0046c1bc;
    FUN_0043d574(3,DAT_0046bb74,DAT_0046bb70,DAT_0046bf60,0xb4,DAT_0046c1bc,puVar1[0x16]);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_0046b762:
    compress_log_output(0xc400000,DAT_0046c1c0,DAT_0046c1c0,puVar1[0x16]);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_0046b762;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0xb5;
    param_3 = DAT_0046c1c4;
    FUN_0043d574(3,DAT_0046bb74,DAT_0046bb70,DAT_0046bf60,0xb5,DAT_0046c1c4,puVar1[0x17]);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_0046b7aa:
    compress_log_output(0xc400000,DAT_0046c214,DAT_0046c214,puVar1[0x17]);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_0046b7aa;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0xb6;
    param_3 = DAT_0046c218;
    FUN_0043d574(3,DAT_0046bb74,DAT_0046bb70,DAT_0046bf60,0xb6,DAT_0046c218,
                 *(undefined4 *)(puVar1 + 0x10));
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_0046b7f2:
    compress_log_output(0xc400000,DAT_0046c21c,DAT_0046c21c,*(undefined4 *)(puVar1 + 0x10));
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_0046b7f2;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0xb7;
    param_3 = DAT_0046c220;
    FUN_0043d574(3,DAT_0046bb74,DAT_0046bb70,DAT_0046bf60,0xb7,DAT_0046c220,
                 *(undefined2 *)(puVar1 + 0x18));
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_0046b83a:
    compress_log_output(0xc400000,DAT_0046c224,DAT_0046c224,*(undefined2 *)(puVar1 + 0x18));
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_0046b83a;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0xb8;
    param_3 = DAT_0046c228;
    FUN_0043d574(3,DAT_0046bb74,DAT_0046bb70,DAT_0046bf60,0xb8,DAT_0046c228,puVar1[0x1d]);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_0046b87e:
    compress_log_output(0xc400000,DAT_0046c22c,DAT_0046c22c,puVar1[0x1d]);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_0046b87e;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0xb9;
    param_3 = DAT_0046c230;
    FUN_0043d574(3,DAT_0046bb74,DAT_0046bb70,DAT_0046bf60,0xb9,DAT_0046c230,
                 *(undefined4 *)(puVar1 + 0x24));
  }
  iVar2 = FUN_0043d0ce();
  if (-1 < iVar2 << 0x1f) {
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1d) goto LAB_0046b8d2;
  }
  compress_log_output(0xc400000,DAT_0046c234,DAT_0046c234,*(undefined4 *)(puVar1 + 0x24));
LAB_0046b8d2:
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0xba;
    param_3 = DAT_0046c238;
    FUN_0043d574(3,DAT_0046bb74,DAT_0046bb70,DAT_0046bf60);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_0046c504,DAT_0046c504);
  }
  return CONCAT44(param_3,param_2);
}

