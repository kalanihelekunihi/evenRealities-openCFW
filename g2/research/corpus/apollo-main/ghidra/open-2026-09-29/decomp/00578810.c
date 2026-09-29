
undefined8
semantic_CodecValidateFirmwareHeader
          (ushort *param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  ushort *puVar2;
  
  puVar2 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_3 = (uint)*param_1;
    puVar2 = (ushort *)0x166;
    param_2 = DAT_00579158;
    FUN_0043d574(4,DAT_00579164,DAT_00579160,DAT_0057915c,0x166,DAT_00579158,param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_0057884e:
    compress_log_output(0x10400000,DAT_00579168,DAT_00579168,*param_1,puVar2,param_2,param_3);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_0057884e;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    puVar2 = (ushort *)0x167;
    param_2 = DAT_0057916c;
    FUN_0043d574(4,DAT_00579164,DAT_00579160,DAT_0057915c,0x167,DAT_0057916c,(char)param_1[1]);
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_00578898:
    compress_log_output(0x10400000,DAT_00579170,DAT_00579170,(char)param_1[1]);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_00578898;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    puVar2 = (ushort *)0x168;
    param_2 = DAT_00579174;
    FUN_0043d574(4,DAT_00579164,DAT_00579160,DAT_0057915c,0x168,DAT_00579174,
                 *(undefined1 *)((int)param_1 + 3));
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_005788e2:
    compress_log_output(0x10400000,DAT_00579178,DAT_00579178,*(undefined1 *)((int)param_1 + 3));
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_005788e2;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    puVar2 = (ushort *)0x169;
    param_2 = DAT_0057917c;
    FUN_0043d574(4,DAT_00579164,DAT_00579160,DAT_0057915c,0x169,DAT_0057917c,param_1[2]);
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_0057892c:
    compress_log_output(0x10400000,DAT_00579180,DAT_00579180,param_1[2]);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_0057892c;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    puVar2 = (ushort *)0x16a;
    param_2 = DAT_00579184;
    FUN_0043d574(4,DAT_00579164,DAT_00579160,DAT_0057915c,0x16a,DAT_00579184,
                 *(undefined4 *)(param_1 + 4));
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_00578976:
    compress_log_output(0x10400000,DAT_00579188,DAT_00579188,*(undefined4 *)(param_1 + 4));
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_00578976;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    puVar2 = (ushort *)0x16b;
    param_2 = DAT_0057918c;
    FUN_0043d574(4,DAT_00579164,DAT_00579160,DAT_0057915c,0x16b,DAT_0057918c,
                 *(undefined4 *)(param_1 + 6));
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_005789c0:
    compress_log_output(0x10400000,DAT_00579190,DAT_00579190,*(undefined4 *)(param_1 + 6));
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_005789c0;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    puVar2 = (ushort *)0x16c;
    param_2 = DAT_00579194;
    FUN_0043d574(4,DAT_00579164,DAT_00579160,DAT_0057915c,0x16c,DAT_00579194,
                 *(undefined4 *)(param_1 + 8));
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_00578a1a;
  }
  compress_log_output(0x10400000,DAT_00579198,DAT_00579198,*(undefined4 *)(param_1 + 8));
LAB_00578a1a:
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    puVar2 = (ushort *)0x16d;
    param_2 = DAT_0057919c;
    FUN_0043d574(4,DAT_00579164,DAT_00579160,DAT_0057915c,0x16d,DAT_0057919c,
                 *(undefined4 *)(param_1 + 10));
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00579638,DAT_00579638,*(undefined4 *)(param_1 + 10));
  }
  return CONCAT44(param_2,puVar2);
}

