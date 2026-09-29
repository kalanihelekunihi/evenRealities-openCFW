
int FUN_0047fea0(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

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
    if ((*DAT_00480188 & 0x3f) >> 4 == 3) {
      iVar3 = 0;
    }
    else {
      local_18 = param_1;
      FUN_00480358();
      FUN_0047fe12();
      *DAT_004801d4 = *DAT_004801d4 | 0x80000000;
      *DAT_004801d8 = *DAT_004801d8 | 0xf;
      FUN_0048036e();
      *DAT_004801dc = *DAT_004801dc | 1;
      FUN_00480384();
    }
  }
  else if (uVar2 == 2) {
    *DAT_004801e0 = *DAT_004801e0 & 0xffffff03 | 0x80;
    *DAT_004801e4 = 1;
  }
  else if (uVar2 < 2) {
    local_18 = param_1 & 0xffffff00;
    FUN_0047f90c(0x17,&local_18);
    if (((local_18 & 0xff) != 0) && (iVar3 = FUN_0047f56e(), iVar3 == 0)) {
      iVar3 = FUN_0047f7ae(0x17);
    }
  }
  else if (uVar2 == 3) {
    *DAT_0048010c = *DAT_0048010c & 0xfeffffff;
    puVar1 = DAT_00480110;
    *DAT_00480110 = *DAT_00480110 & 0xfffffffe;
    *puVar1 = *puVar1 & 0xfffffff1;
    *DAT_004801e8 = 0;
    *DAT_004801ec = 0;
    local_18 = 1;
    iVar3 = FUN_00480826(5,DAT_004801e8,0x3fffffff,0);
    if (iVar3 == 0) {
      local_10 = 0;
      FUN_00480312(3,0,&local_10);
      local_18 = 1;
      iVar3 = FUN_00480826(5,DAT_004801ec,0x4c4,0);
      if (iVar3 == 0) {
        local_14 = 0;
        FUN_00480312(4,0,&local_14);
      }
    }
  }
  else {
    iVar3 = 6;
  }
  return iVar3;
}

