
undefined8
cff_encoding_load(uint *param_1,int param_2,uint param_3,int param_4,int param_5,uint param_6)

{
  byte bVar1;
  short sVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  byte *pbVar8;
  uint uVar9;
  uint uVar10;
  int local_28;
  
  local_28 = 0;
  if (*(int *)(param_2 + 8) == 0) {
    local_28 = 3;
  }
  else {
    for (uVar6 = 0; uVar6 < 0x100; uVar6 = uVar6 + 1) {
      pbVar8 = (byte *)((int)param_1 + uVar6 * 2 + 0xc);
      pbVar8[0] = 0;
      pbVar8[1] = 0;
      pbVar8 = (byte *)((int)param_1 + uVar6 * 2 + 0x20c);
      pbVar8[0] = 0;
      pbVar8[1] = 0;
    }
    if (param_6 < 2) {
      if (param_6 == 0) {
        FUN_00439be4(param_1 + 3,DAT_005af418,0x200);
      }
      else {
        if (param_6 != 1) {
          local_28 = 3;
          goto LAB_005aea8a;
        }
        FUN_00439be4(param_1 + 3,DAT_005af41c,0x200);
      }
      param_1[2] = 0;
      local_28 = cff_charset_compute_cids(param_2,param_3,*(undefined4 *)(param_4 + 0x1c));
      if (local_28 == 0) {
        for (uVar6 = 0; uVar6 < 0x100; uVar6 = uVar6 + 1) {
          iVar5 = 0;
          if (*(short *)((int)param_1 + uVar6 * 2 + 0xc) != 0) {
            iVar5 = cff_charset_cid_to_gindex(param_2);
          }
          if (iVar5 == 0) {
            pbVar8 = (byte *)((int)param_1 + uVar6 * 2 + 0x20c);
            pbVar8[0] = 0;
            pbVar8[1] = 0;
            pbVar8 = (byte *)((int)param_1 + uVar6 * 2 + 0xc);
            pbVar8[0] = 0;
            pbVar8[1] = 0;
          }
          else {
            *(short *)((int)param_1 + uVar6 * 2 + 0x20c) = (short)iVar5;
            param_1[2] = uVar6 + 1;
          }
        }
      }
    }
    else {
      param_1[1] = param_6 + param_5;
      local_28 = FT_Stream_Seek(param_4,param_1[1]);
      if (local_28 == 0) {
        bVar1 = FT_Stream_ReadChar(param_4,&local_28);
        *param_1 = (uint)bVar1;
        if (local_28 == 0) {
          uVar6 = FT_Stream_ReadChar(param_4,&local_28);
          uVar6 = uVar6 & 0xff;
          if (local_28 == 0) {
            if ((*param_1 & 0x7f) == 0) {
              param_1[2] = uVar6 + 1;
              local_28 = FT_Stream_EnterFrame(param_4,uVar6);
              if (local_28 != 0) goto LAB_005aea8a;
              pbVar8 = *(byte **)(param_4 + 0x20);
              for (uVar10 = 1; uVar10 <= uVar6; uVar10 = uVar10 + 1) {
                bVar1 = *pbVar8;
                pbVar8 = pbVar8 + 1;
                if (uVar10 < param_3) {
                  *(short *)((int)param_1 + (uint)bVar1 * 2 + 0x20c) = (short)uVar10;
                  *(undefined2 *)((int)param_1 + (uint)bVar1 * 2 + 0xc) =
                       *(undefined2 *)(*(int *)(param_2 + 8) + uVar10 * 2);
                }
              }
              FT_Stream_ExitFrame(param_4);
            }
            else {
              if ((*param_1 & 0x7f) != 1) {
                local_28 = 3;
                goto LAB_005aea8a;
              }
              uVar10 = 1;
              param_1[2] = 0;
              for (uVar9 = 0; uVar9 < uVar6; uVar9 = uVar9 + 1) {
                uVar3 = FT_Stream_ReadChar(param_4,&local_28);
                uVar3 = uVar3 & 0xff;
                if (local_28 != 0) goto LAB_005aea8a;
                uVar4 = FT_Stream_ReadChar(param_4,&local_28);
                if (local_28 != 0) goto LAB_005aea8a;
                uVar7 = (uVar4 & 0xff) + 1;
                uVar4 = uVar10;
                if (param_1[2] < uVar7) {
                  param_1[2] = uVar7;
                }
                for (; uVar4 < uVar10 + uVar7; uVar4 = uVar4 + 1) {
                  if ((uVar4 < param_3) && (uVar3 < 0x100)) {
                    *(short *)((int)param_1 + uVar3 * 2 + 0x20c) = (short)uVar4;
                    *(undefined2 *)((int)param_1 + uVar3 * 2 + 0xc) =
                         *(undefined2 *)(*(int *)(param_2 + 8) + uVar4 * 2);
                  }
                  uVar3 = uVar3 + 1;
                }
                uVar10 = uVar7 + uVar10;
              }
              if (0x100 < param_1[2]) {
                param_1[2] = 0x100;
              }
            }
            if ((int)((uint)(byte)*param_1 << 0x18) < 0) {
              uVar6 = FT_Stream_ReadChar(param_4,&local_28);
              if (local_28 == 0) {
                for (uVar10 = 0; uVar10 < (uVar6 & 0xff); uVar10 = uVar10 + 1) {
                  uVar9 = FT_Stream_ReadChar(param_4,&local_28);
                  if ((local_28 != 0) ||
                     (sVar2 = FT_Stream_ReadUShort(param_4,&local_28), local_28 != 0)) break;
                  *(short *)((int)param_1 + (uVar9 & 0xff) * 2 + 0xc) = sVar2;
                  for (uVar3 = 0; uVar3 < param_3; uVar3 = uVar3 + 1) {
                    if (*(short *)(*(int *)(param_2 + 8) + uVar3 * 2) == sVar2) {
                      *(short *)((int)param_1 + (uVar9 & 0xff) * 2 + 0x20c) = (short)uVar3;
                      break;
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
LAB_005aea8a:
  return CONCAT44(local_28,local_28);
}

