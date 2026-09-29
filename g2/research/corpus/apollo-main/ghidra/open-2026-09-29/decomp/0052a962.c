
byte * hciCoreAclReassembly(byte *param_1)

{
  undefined1 uVar1;
  short sVar2;
  bool bVar3;
  int iVar4;
  undefined4 uVar5;
  undefined1 *puVar6;
  char *pcVar7;
  int iVar8;
  byte *pbVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  int iVar13;
  
  pbVar9 = (byte *)0x0;
  bVar3 = true;
  uVar10 = (uint)param_1[1] * 0x100 + (uint)*param_1;
  uVar12 = uVar10 & 0x3000;
  uVar10 = uVar10 & 0xfff;
  uVar11 = (uint)param_1[3] * 0x100 + (uint)param_1[2];
  iVar4 = hciCoreConnByHandle(uVar10);
  if (iVar4 != 0) {
    sVar2 = (short)uVar11;
    if (uVar12 == 0x2000) {
      if (*(int *)(iVar4 + 8) != 0) {
        WsfMsgFree(*(undefined4 *)(iVar4 + 8));
        *(undefined4 *)(iVar4 + 8) = 0;
      }
      iVar13 = DAT_0052ae14;
      uVar1 = (undefined1)(uVar10 >> 8);
      if (uVar11 < 2) {
        if (uVar11 != 0) {
          uVar5 = WsfMsgDataAlloc(*(short *)(DAT_0052ae14 + 0x7c) + 4,0);
          *(undefined4 *)(iVar4 + 8) = uVar5;
          if (*(int *)(iVar4 + 8) != 0) {
            *(undefined4 *)(iVar4 + 0xc) = *(undefined4 *)(iVar4 + 8);
            puVar6 = *(undefined1 **)(iVar4 + 0xc);
            *(undefined1 **)(iVar4 + 0xc) = puVar6 + 1;
            *puVar6 = (char)uVar10;
            puVar6 = *(undefined1 **)(iVar4 + 0xc);
            *(undefined1 **)(iVar4 + 0xc) = puVar6 + 1;
            *puVar6 = uVar1;
            puVar6 = *(undefined1 **)(iVar4 + 0xc);
            *(undefined1 **)(iVar4 + 0xc) = puVar6 + 1;
            *puVar6 = 0;
            puVar6 = *(undefined1 **)(iVar4 + 0xc);
            *(undefined1 **)(iVar4 + 0xc) = puVar6 + 1;
            *puVar6 = 0;
            FUN_00439be4(*(undefined4 *)(iVar4 + 0xc),param_1 + 4,uVar11);
            *(uint *)(iVar4 + 0xc) = *(int *)(iVar4 + 0xc) + uVar11;
            *(short *)(iVar4 + 0x14) = *(short *)(iVar13 + 0x7c) - sVar2;
          }
        }
      }
      else {
        iVar13 = (uint)param_1[5] * 0x100 + (uint)param_1[4];
        if (iVar13 + 4U <= (uint)*(ushort *)(DAT_0052ae14 + 0x7c)) {
          if (uVar11 < iVar13 + 4U) {
            uVar5 = WsfMsgDataAlloc(iVar13 + 8U & 0xffff,0);
            *(undefined4 *)(iVar4 + 8) = uVar5;
            if (*(int *)(iVar4 + 8) != 0) {
              *(undefined4 *)(iVar4 + 0xc) = *(undefined4 *)(iVar4 + 8);
              puVar6 = *(undefined1 **)(iVar4 + 0xc);
              *(undefined1 **)(iVar4 + 0xc) = puVar6 + 1;
              *puVar6 = (char)uVar10;
              puVar6 = *(undefined1 **)(iVar4 + 0xc);
              *(undefined1 **)(iVar4 + 0xc) = puVar6 + 1;
              *puVar6 = uVar1;
              pcVar7 = *(char **)(iVar4 + 0xc);
              *(char **)(iVar4 + 0xc) = pcVar7 + 1;
              *pcVar7 = (char)iVar13 + '\x04';
              puVar6 = *(undefined1 **)(iVar4 + 0xc);
              *(undefined1 **)(iVar4 + 0xc) = puVar6 + 1;
              *puVar6 = (char)((uint)(iVar13 + 4) >> 8);
              if (2 < uVar11) {
                FUN_00439be4(*(undefined4 *)(iVar4 + 0xc),param_1 + 4,uVar11);
              }
              *(uint *)(iVar4 + 0xc) = *(int *)(iVar4 + 0xc) + uVar11;
              *(short *)(iVar4 + 0x14) = ((short)iVar13 + 4) - sVar2;
            }
          }
          else {
            bVar3 = false;
            pbVar9 = param_1;
          }
        }
      }
    }
    else if ((uVar12 == 0x1000) && (*(int *)(iVar4 + 8) != 0)) {
      if (*(ushort *)(iVar4 + 0x14) < uVar11) {
        WsfMsgFree(*(undefined4 *)(iVar4 + 8));
        *(undefined4 *)(iVar4 + 8) = 0;
      }
      else {
        FUN_00439be4(*(undefined4 *)(iVar4 + 0xc),param_1 + 4,uVar11);
        iVar13 = DAT_0052ae14;
        if (*(int *)(iVar4 + 0xc) - *(int *)(iVar4 + 8) < 6) {
          iVar8 = (uint)*(byte *)(*(int *)(iVar4 + 8) + 5) * 0x100 +
                  (uint)*(byte *)(*(int *)(iVar4 + 8) + 4);
          if ((uint)*(ushort *)(DAT_0052ae14 + 0x7c) < iVar8 + 4U) {
            WsfMsgFree(*(undefined4 *)(iVar4 + 8));
            *(undefined4 *)(iVar4 + 8) = 0;
          }
          else {
            *(char *)(*(int *)(iVar4 + 8) + 2) = (char)iVar8 + '\x04';
            *(char *)(*(int *)(iVar4 + 8) + 3) = (char)((uint)(iVar8 + 4) >> 8);
            *(short *)(iVar4 + 0x14) =
                 (short)iVar8 + (*(short *)(iVar4 + 0x14) - *(short *)(iVar13 + 0x7c)) + 4;
          }
        }
        *(uint *)(iVar4 + 0xc) = *(int *)(iVar4 + 0xc) + uVar11;
        *(short *)(iVar4 + 0x14) = *(short *)(iVar4 + 0x14) - sVar2;
        if (*(short *)(iVar4 + 0x14) == 0) {
          pbVar9 = *(byte **)(iVar4 + 8);
          *(undefined4 *)(iVar4 + 8) = 0;
        }
      }
    }
  }
  if (bVar3) {
    WsfMsgFree(param_1);
  }
  return pbVar9;
}

