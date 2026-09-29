
int TT_Process_Composite_Glyph(int *param_1,int param_2,uint param_3,undefined4 param_4)

{
  ushort uVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  int *piVar5;
  int iVar6;
  int local_24;
  uint local_20;
  undefined4 uStack_1c;
  
  iVar2 = param_1[3];
  local_20 = param_3;
  uStack_1c = param_4;
  if ((*(short *)(iVar2 + 0x16) == -4) ||
     ((uint)(*(short *)(iVar2 + 0x16) + 4 +
            (int)*(short *)(param_1[3] + 0x3a) + (int)*(short *)(param_1[3] + 0x16)) <=
      *(uint *)(param_1[3] + 4))) {
    local_24 = 0;
  }
  else {
    local_24 = param_2;
    local_24 = FT_GlyphLoader_CheckPoints(param_1[3],*(short *)(iVar2 + 0x16) + 4,0,param_4,param_1)
    ;
  }
  if (local_24 == 0) {
    piVar5 = (int *)(*(int *)(iVar2 + 0x18) + *(short *)(iVar2 + 0x16) * 8);
    iVar4 = param_1[0x12];
    *piVar5 = param_1[0x11];
    piVar5[1] = iVar4;
    iVar6 = *(int *)(iVar2 + 0x18) + *(short *)(iVar2 + 0x16) * 8;
    iVar4 = param_1[0x14];
    *(int *)(iVar6 + 8) = param_1[0x13];
    *(int *)(iVar6 + 0xc) = iVar4;
    iVar6 = *(int *)(iVar2 + 0x18) + *(short *)(iVar2 + 0x16) * 8;
    iVar4 = param_1[0x2e];
    *(int *)(iVar6 + 0x10) = param_1[0x2d];
    *(int *)(iVar6 + 0x14) = iVar4;
    iVar6 = *(int *)(iVar2 + 0x18) + *(short *)(iVar2 + 0x16) * 8;
    iVar4 = param_1[0x30];
    *(int *)(iVar6 + 0x18) = param_1[0x2f];
    *(int *)(iVar6 + 0x1c) = iVar4;
    *(undefined1 *)(*(int *)(iVar2 + 0x1c) + (int)*(short *)(iVar2 + 0x16)) = 0;
    *(undefined1 *)(*(int *)(iVar2 + 0x1c) + (int)*(short *)(iVar2 + 0x16) + 1) = 0;
    *(undefined1 *)(*(int *)(iVar2 + 0x1c) + (int)*(short *)(iVar2 + 0x16) + 2) = 0;
    *(undefined1 *)(*(int *)(iVar2 + 0x1c) + (int)*(short *)(iVar2 + 0x16) + 3) = 0;
    iVar2 = param_1[6];
    local_24 = FT_Stream_Seek(iVar2,param_1[0x29]);
    if ((local_24 == 0) && (uVar1 = FT_Stream_ReadUShort(iVar2,&local_24), local_24 == 0)) {
      if (*(ushort *)(*param_1 + 0x11e) < uVar1) {
        if (param_1[7] < (int)(uint)uVar1) {
          return 0x16;
        }
        local_20 = *(uint *)(param_1[0x27] + 0x188);
        local_24 = Update_Max(*(undefined4 *)(param_1[0x27] + 8),&local_20,1,param_1[0x27] + 0x18c,
                              uVar1);
        *(uint *)(param_1[0x27] + 0x188) = local_20 & 0xffff;
        if (local_24 != 0) {
          return local_24;
        }
      }
      else if (uVar1 == 0) {
        return 0;
      }
      local_24 = FT_Stream_Read(iVar2,*(undefined4 *)(param_1[0x27] + 0x18c),uVar1);
      if (local_24 == 0) {
        *(undefined4 *)(param_1[2] + 0x88) = *(undefined4 *)(param_1[0x27] + 0x18c);
        *(uint *)(param_1[2] + 0x8c) = (uint)uVar1;
        tt_prepare_zone(param_1 + 0x1e,param_1[3] + 0x14,param_2,param_3);
        for (uVar3 = 0; uVar3 < *(ushort *)(param_1 + 0x20); uVar3 = uVar3 + 1) {
          *(byte *)(param_1[0x24] + uVar3) = *(byte *)(param_1[0x24] + uVar3) & 0xe7;
        }
        *(short *)(param_1 + 0x20) = (short)param_1[0x20] + 4;
        local_24 = TT_Hint_Glyph(param_1,1);
      }
    }
  }
  return local_24;
}

