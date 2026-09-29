
void FUN_004f7fa8(void)

{
  int *piVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 in_r3;
  undefined4 uVar4;
  undefined4 local_70;
  undefined4 local_6c;
  int local_68;
  undefined4 local_60;
  undefined4 local_40;
  undefined4 uStack_10;
  
  puVar2 = DAT_004f88d4;
  piVar1 = DAT_004f81e4;
  if ((*DAT_004f8090 != 0) && (-1 < *DAT_004f81e4)) {
    *DAT_004f88d4 = 1;
    uStack_10 = in_r3;
    if ((*piVar1 < 0) ||
       ((((int)(uint)*DAT_004f8628 <= *piVar1 || (0x27 < *piVar1)) ||
        (*(int *)(DAT_004f8638 + *piVar1 * 0x10) == 0)))) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_68 = *piVar1;
        local_6c = DAT_004f88d8;
        local_70 = 0xb27;
        FUN_0043d574(2,DAT_004f81e0,DAT_004f81dc,DAT_004f88dc);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_004f88e0,DAT_004f88e0,*piVar1);
      }
      *puVar2 = 0;
      FUN_004f6a10(0);
    }
    else {
      uVar4 = *(undefined4 *)(DAT_004f8638 + *piVar1 * 0x10);
      FUN_00441488(uVar4,0,0);
      FUN_004503d6(&local_70);
      local_70 = uVar4;
      FUN_004506ce(&local_70,0,0xff);
      local_40 = 100;
      local_6c = DAT_004f88e4;
      local_60 = DAT_004f88e8;
      FUN_00450408(&local_70);
    }
  }
  return;
}

