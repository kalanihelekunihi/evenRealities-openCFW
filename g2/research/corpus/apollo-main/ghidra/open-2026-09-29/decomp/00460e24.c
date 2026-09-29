
void FUN_00460e24(void)

{
  int *piVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  uint uVar7;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  
  uVar2 = FUN_0044e4aa(*DAT_00461b10);
  piVar1 = DAT_00461b70;
  uVar3 = FUN_00460d6c(*DAT_00461b70);
  iVar4 = FUN_0043d0ce();
  iVar6 = DAT_004615a0;
  if (iVar4 << 0x1e < 0) {
    uVar5 = FUN_00460084(*piVar1 * 0x34 + DAT_004615a0 + 4);
    local_24 = FUN_0045fffe(iVar6 + *piVar1 * 0x34 + 4,uVar5);
    local_20 = uVar2;
    local_1c = uVar3;
    FUN_0043d574(4,DAT_004611c0,DAT_004611bc,DAT_004615a8,0x204,DAT_004615a4,*piVar1);
  }
  iVar6 = FUN_0043d0ce();
  if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
    iVar6 = DAT_004615a0;
    uVar5 = FUN_00460084(*piVar1 * 0x34 + DAT_004615a0 + 4);
    uVar5 = FUN_0045fffe(iVar6 + *piVar1 * 0x34 + 4,uVar5);
    compress_log_output(0x11000000,DAT_004615ac,DAT_004615ac,*piVar1,uVar5,uVar2,uVar3);
  }
  FUN_00462db6();
  FUN_00462db4();
  *DAT_004615b0 = 0;
  iVar6 = FUN_004602b6();
  if (iVar6 == 0) {
    FUN_0043c0e4(&local_24,10,0);
    FUN_004602ca(&local_24,5);
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004611c0,DAT_004611bc,DAT_004615a8,0x20c,DAT_004615b4,local_24 & 0xff);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004615b8,DAT_004615b8,local_24 & 0xff);
    }
    uVar7 = local_24 & 0xff;
    if (uVar7 == 10) {
      FUN_00461620(2);
    }
    else if (uVar7 == 0x44) {
      FUN_00461620(1);
    }
    else if (uVar7 == 0x45) {
      FUN_00461620(0);
    }
    else if (uVar7 == 0x46) {
      FUN_00462594(local_24._1_1_);
    }
    else if ((uVar7 == 0x48) && (iVar6 = FUN_0045a568(), iVar6 == 1)) {
      FUN_00464c36(3,0,0,0);
    }
  }
  return;
}

