
undefined8 FUN_004f7408(uint param_1,undefined4 param_2,uint param_3,uint param_4)

{
  int iVar1;
  int iVar2;
  
  iVar1 = DAT_004f7c90;
  if ((*(char *)(DAT_004f7c90 + 0x2e4e) == '\0') || (*(short *)(DAT_004f7c90 + 0x2e48) == 0))
  goto LAB_004f7474;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_4 = (uint)*(ushort *)(iVar1 + 0x2e48);
    param_3 = (uint)*(byte *)(iVar1 + 0x2e4e);
    param_1 = 0x8ab;
    param_2 = DAT_004f7ea8;
    FUN_0043d574(4,DAT_004f758c,DAT_004f7588,DAT_004f7eac,0x8ab,DAT_004f7ea8,param_3,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_004f745c:
    param_1 = (uint)*(ushort *)(iVar1 + 0x2e48);
    compress_log_output(0x10800000,DAT_004f808c,DAT_004f808c,*(undefined1 *)(iVar1 + 0x2e4e),param_1
                        ,param_2,param_3,param_4);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_004f745c;
  }
  FUN_004f7fa8();
LAB_004f7474:
  return CONCAT44(param_2,param_1);
}

