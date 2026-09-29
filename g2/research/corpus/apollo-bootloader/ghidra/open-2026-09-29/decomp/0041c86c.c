
int FUN_0041c86c(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint *puVar1;
  uint uVar2;
  int iVar3;
  uint local_18;
  undefined4 local_14;
  undefined4 local_10;
  undefined4 uStack_c;
  
  iVar3 = 0;
  uVar2 = param_1 & 0xff;
  local_14 = param_2;
  local_10 = param_3;
  uStack_c = param_4;
  if (uVar2 == 0) {
    if ((*DAT_0041cb8c & 0x3f) >> 4 == 3) {
      iVar3 = 0;
    }
    else {
      local_18 = param_1;
      FUN_0041cd76();
      FUN_0041c7de();
      *DAT_0041cbd8 = *DAT_0041cbd8 | 0x80000000;
      *DAT_0041cbdc = *DAT_0041cbdc | 0xf;
      FUN_0041cd8c();
      *DAT_0041cbe0 = *DAT_0041cbe0 | 1;
      FUN_0041cda2();
    }
  }
  else if (uVar2 == 2) {
    *DAT_0041cbe4 = *DAT_0041cbe4 & 0xffffff03 | 0x80;
    *DAT_0041cbe8 = 1;
  }
  else if (uVar2 < 2) {
    local_18 = param_1 & 0xffffff00;
    FUN_0041c2d8(0x17,&local_18);
    if (((local_18 & 0xff) != 0) && (iVar3 = FUN_0041bf3a(), iVar3 == 0)) {
      iVar3 = FUN_0041c17a(0x17);
    }
  }
  else if (uVar2 == 3) {
    *DAT_0041cb10 = *DAT_0041cb10 & 0xfeffffff;
    puVar1 = DAT_0041cb14;
    *DAT_0041cb14 = *DAT_0041cb14 & 0xfffffffe;
    *puVar1 = *puVar1 & 0xfffffff1;
    *DAT_0041cbec = 0;
    *DAT_0041cbf0 = 0;
    local_18 = 1;
    iVar3 = delay_us_status_check(5,DAT_0041cbec,0x3fffffff,0);
    if (iVar3 == 0) {
      local_10 = 0;
      FUN_0041cd1a(3,0,&local_10);
      local_18 = 1;
      iVar3 = delay_us_status_check(5,DAT_0041cbf0,0x4c4,0);
      if (iVar3 == 0) {
        local_14 = 0;
        FUN_0041cd1a(4,0,&local_14);
      }
    }
  }
  else {
    iVar3 = 6;
  }
  return iVar3;
}

