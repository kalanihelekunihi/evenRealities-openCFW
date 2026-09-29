
void FUN_004c2e30(uint param_1,byte param_2)

{
  undefined4 *puVar1;
  uint uVar2;
  
  puVar1 = DAT_004c3224;
  if (param_1 < 8) {
    uVar2 = (uint)param_2 | param_1 << 2;
    if (uVar2 == 0) {
      FUN_00480f0c(5,*DAT_004c3224);
      FUN_00480f0c(7,*puVar1);
      FUN_00480f0c(6,*puVar1);
      FUN_00480f0c(0x32,*puVar1);
    }
    else if (uVar2 == 1) {
      FUN_00480f0c(5,*DAT_004c3224);
      FUN_00480f0c(6,*puVar1);
    }
    else if (uVar2 == 4) {
      FUN_00480f0c(8,*DAT_004c3224);
      FUN_00480f0c(10,*puVar1);
      FUN_00480f0c(9,*puVar1);
      FUN_00480f0c(0x33,*puVar1);
    }
    else if (uVar2 == 5) {
      FUN_00480f0c(8,*DAT_004c3224);
      FUN_00480f0c(9,*puVar1);
    }
    else if (uVar2 == 8) {
      FUN_00480f0c(0x19,*DAT_004c3224);
      FUN_00480f0c(0x1b,*puVar1);
      FUN_00480f0c(0x1a,*puVar1);
      FUN_00480f0c(0xb,*puVar1);
    }
    else if (uVar2 == 9) {
      FUN_00480f0c(0x19,*DAT_004c3224);
      FUN_00480f0c(0x1a,*puVar1);
    }
    else if (uVar2 == 0xc) {
      FUN_00480f0c(0x1f,*DAT_004c3224);
      FUN_00480f0c(0x21,*puVar1);
      FUN_00480f0c(0x20,*puVar1);
      FUN_00480f0c(0xd,*puVar1);
    }
    else if (uVar2 == 0xd) {
      FUN_00480f0c(0x1f,*DAT_004c3224);
      FUN_00480f0c(0x20,*puVar1);
    }
    else if (uVar2 == 0x10) {
      FUN_00480f0c(0x22,*DAT_004c3224);
      FUN_00480f0c(0x24,*puVar1);
      FUN_00480f0c(0x23,*puVar1);
      FUN_00480f0c(0x10,*puVar1);
    }
    else if (uVar2 == 0x11) {
      FUN_00480f0c(0x22,*DAT_004c3224);
      FUN_00480f0c(0x23,*puVar1);
    }
    else if (uVar2 == 0x14) {
      FUN_00480f0c(0x2f,*DAT_004c3224);
      FUN_00480f0c(0x31,*puVar1);
      FUN_00480f0c(0x30,*puVar1);
      FUN_00480f0c(0x11,*puVar1);
    }
    else if (uVar2 == 0x15) {
      FUN_00480f0c(0x2f,*DAT_004c3224);
      FUN_00480f0c(0x30,*puVar1);
    }
    else if (uVar2 == 0x18) {
      FUN_00480f0c(0x3d,*DAT_004c3224);
      FUN_00480f0c(0x3f,*puVar1);
      FUN_00480f0c(0x3e,*puVar1);
      FUN_00480f0c(0x75,*puVar1);
    }
    else if (uVar2 == 0x19) {
      FUN_00480f0c(0x3d,*DAT_004c3224);
      FUN_00480f0c(0x3e,*puVar1);
    }
    else if (uVar2 == 0x1c) {
      FUN_00480f0c(0x16,*DAT_004c3224);
      FUN_00480f0c(0x18,*puVar1);
      FUN_00480f0c(0x17,*puVar1);
      FUN_00480f0c(0x13,*puVar1);
    }
    else if (uVar2 == 0x1d) {
      FUN_00480f0c(0x16,*DAT_004c3224);
      FUN_00480f0c(0x17,*puVar1);
    }
  }
  return;
}

