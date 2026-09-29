
void FUN_004f7794(void)

{
  int *piVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 uVar4;
  int local_1c;
  undefined4 local_18;
  undefined4 local_14;
  int local_10;
  
  piVar1 = DAT_004f7ae0;
  uVar4 = *DAT_004f81e4;
  if (*DAT_004f7ae0 != 0) {
    FUN_0043ded4(*DAT_004f7ae0,1);
    FUN_0043f142(*piVar1,0);
    FUN_00441488(*piVar1,0xff,0);
  }
  puVar2 = DAT_004f8090;
  FUN_0043f66c(*DAT_004f8090);
  FUN_004f6fc4(uVar4,&local_10,&local_1c,&local_14,&local_18);
  iVar3 = FUN_0044e498(*puVar2);
  puVar2 = DAT_004f8094;
  local_1c = local_1c - iVar3;
  FUN_0043f09a(*DAT_004f8094,local_10 + 0xc,local_1c + 8);
  FUN_0043f4c0(*puVar2,local_14,local_18);
  FUN_004f7634(0xff,100,&LAB_004f78cc_1);
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004f81e0,DAT_004f81dc,DAT_004f81ec,0x983,DAT_004f81e8,uVar4);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004f84b8,DAT_004f84b8,uVar4);
  }
  return;
}

