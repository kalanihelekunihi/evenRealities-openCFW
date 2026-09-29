
int tt_loader_init(int *param_1,int param_2,int param_3,uint param_4,char param_5)

{
  byte bVar1;
  byte bVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined4 uVar8;
  uint uVar9;
  char cVar10;
  char cVar11;
  bool bVar12;
  bool bVar13;
  
  bVar1 = (byte)param_4 & 0x80;
  iVar3 = *(int *)(*(int *)(param_3 + 4) + 0x60);
  iVar4 = *(int *)(param_3 + 4);
  iVar5 = *(int *)(iVar4 + 0x68);
  FUN_0043c0e4(param_1,0xd4,0);
  if ((-1 < (int)(param_4 << 0x1e)) && (param_5 == '\0')) {
    bVar13 = false;
    if ((*(int *)(param_2 + 0x130) < 0) || (*(int *)(param_2 + 0x134) < 0)) {
      iVar6 = tt_size_ready_bytecode(param_2,bVar1);
      if (iVar6 != 0) {
        return iVar6;
      }
    }
    else {
      if (*(int *)(param_2 + 0x130) != 0) {
        return *(int *)(param_2 + 0x130);
      }
      if (*(int *)(param_2 + 0x134) != 0) {
        return *(int *)(param_2 + 0x134);
      }
    }
    iVar6 = *(int *)(param_2 + 300);
    if (iVar6 == 0) {
      return 0x99;
    }
    uVar9 = (int)param_4 >> 0x10;
    if (*(int *)(iVar3 + 0x40) == 0x28) {
      bVar12 = (uVar9 & 0xf) != 2;
      if ((bVar12) && ((param_4 & 0x70000) == 0)) {
        cVar10 = '\x01';
      }
      else {
        cVar10 = '\0';
      }
      if (bVar12) {
        bVar2 = (byte)((param_4 << 0xd) >> 0x1f);
      }
      else {
        bVar2 = 0;
      }
      *(byte *)(iVar6 + 0x266) = bVar2;
    }
    else {
      bVar12 = false;
      cVar10 = '\0';
      *(undefined1 *)(iVar6 + 0x266) = 0;
    }
    if (*(int *)(iVar3 + 0x40) == 0x28) {
      if ((bVar12) || ((uVar9 & 0xf) == 2)) {
        cVar11 = '\0';
      }
      else {
        cVar11 = '\x01';
      }
    }
    else if ((uVar9 & 0xf) == 2) {
      cVar11 = '\0';
    }
    else {
      cVar11 = '\x01';
    }
    iVar7 = TT_Load_Context(iVar6,iVar4,param_2);
    if (iVar7 != 0) {
      return iVar7;
    }
    if (*(int *)(iVar3 + 0x40) == 0x28) {
      bVar13 = bVar12 != (bool)*(char *)(iVar6 + 0x265);
      if (bVar13) {
        *(bool *)(iVar6 + 0x265) = bVar12;
      }
      if (cVar10 != *(char *)(iVar6 + 0x26a)) {
        *(char *)(iVar6 + 0x26a) = cVar10;
        bVar13 = true;
      }
    }
    if (cVar11 != *(char *)(iVar6 + 0x264)) {
      *(char *)(iVar6 + 0x264) = cVar11;
      bVar13 = true;
    }
    if (bVar13) {
      for (uVar9 = 0; uVar9 < *(uint *)(param_2 + 0xf8); uVar9 = uVar9 + 1) {
        uVar8 = FT_MulFix((int)*(short *)(*(int *)(iVar4 + 0x29c) + uVar9 * 2),
                          *(undefined4 *)(param_2 + 0x5c));
        *(undefined4 *)(*(int *)(param_2 + 0xfc) + uVar9 * 4) = uVar8;
      }
      iVar3 = tt_size_run_prep(param_2,bVar1);
      if (iVar3 != 0) {
        return iVar3;
      }
    }
    if ((int)((uint)*(byte *)(iVar6 + 0x154) << 0x1f) < 0) {
      param_4 = param_4 | 2;
    }
    if ((int)((uint)*(byte *)(iVar6 + 0x154) << 0x1e) < 0) {
      FUN_00439c04(iVar6 + 0x120,DAT_005f1ba0,0x44);
    }
    *(byte *)(iVar6 + 0x235) = (byte)param_4 & 0x80;
    param_1[0x27] = iVar6;
    param_1[0x28] = *(int *)(iVar6 + 0x18c);
  }
  if (param_5 == '\0') {
    iVar3 = **(int **)(param_3 + 0x9c);
    FT_GlyphLoader_Rewind(iVar3);
    param_1[3] = iVar3;
  }
  param_1[4] = param_4;
  *param_1 = iVar4;
  param_1[1] = param_2;
  param_1[2] = param_3;
  param_1[6] = iVar5;
  param_1[0x33] = 0;
  param_1[0x34] = 0;
  return 0;
}

