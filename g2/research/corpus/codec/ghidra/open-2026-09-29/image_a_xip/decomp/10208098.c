
undefined4 gx8002_uart_receive_callback(uint param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  uint *puVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  int iVar9;
  uint *puVar10;
  int iVar11;
  int *piVar12;
  int iVar13;
  int *piVar14;
  uint uStack_30;
  
  puVar3 = (uint *)gx8002_channel_lookup(param_1 & 0xff);
  iVar1 = DAT_1020829c;
  if (puVar3 == (uint *)0x0) {
    uVar4 = 0xffffffff;
  }
  else {
    iVar11 = DAT_1020829c + 0x4d0;
    *(int *)(DAT_1020829c + 0x588) = iVar11;
    uStack_30 = gx8002_uart_read(param_1,iVar11,param_2);
    iVar2 = DAT_102082a0;
    if (uStack_30 != 0) {
      puVar10 = puVar3 + 7;
      iVar13 = iVar1 + param_1 * 4;
      do {
        uVar8 = puVar3[0x5c];
        if (uVar8 == 1) {
          iVar7 = *(int *)(iVar1 + 0x588);
          for (uVar8 = 0;
              (uVar8 != uStack_30 && (uVar6 = *(int *)(iVar2 + param_1 * 4) + uVar8, uVar6 < 0xe));
              uVar8 = uVar8 + 1) {
            *(undefined1 *)((int)puVar10 + uVar6) = *(undefined1 *)(iVar7 + uVar8);
          }
          iVar7 = *(int *)(iVar2 + param_1 * 4) + uVar8;
          uStack_30 = uStack_30 - uVar8;
          *(int *)(iVar2 + param_1 * 4) = iVar7;
          if (uStack_30 != 0) {
            *(uint *)(iVar1 + 0x588) = uVar8 + *(int *)(iVar1 + 0x588);
          }
          if (iVar7 != 0xe) goto LAB_10208118;
          *(undefined4 *)(iVar2 + param_1 * 4) = 4;
          iVar7 = *(int *)((int)puVar3 + 0x26);
          iVar9 = crc32(0,puVar10,10);
          if (iVar7 == iVar9) {
            if ((short)puVar3[9] == 0) {
              puVar3[0x5c] = 0;
              *(char *)(puVar3 + 0xc) = (char)param_1;
              puVar3[0xd] = 0;
              goto LAB_1020828a;
            }
            uVar8 = 2;
          }
          else {
            uVar8 = 0;
            *(undefined1 *)puVar10 = 0;
            *(undefined1 *)((int)puVar3 + 0x1d) = 0;
            *(undefined1 *)((int)puVar3 + 0x1e) = 0;
            *(undefined1 *)((int)puVar3 + 0x1f) = 0;
          }
LAB_102081b0:
          puVar3[0x5c] = uVar8;
        }
        else {
          if (uVar8 == 0) {
            if (*puVar3 != puVar3[7]) {
              iVar7 = *(int *)(iVar1 + 0x588);
              uVar8 = 0;
              do {
                uVar6 = uVar8;
                if (uVar6 == uStack_30) {
                  uStack_30 = 0;
                  *(int *)(iVar1 + 0x588) = iVar11;
                  goto LAB_10208118;
                }
                uVar5 = puVar3[7] >> 8 | (uint)*(byte *)(iVar7 + uVar6) << 0x18;
                puVar3[7] = uVar5;
                uVar8 = uVar6 + 1;
              } while (*puVar3 != uVar5);
              uStack_30 = (uStack_30 - 1) - uVar6;
              *(uint *)(iVar1 + 0x588) = iVar7 + uVar6 + 1;
            }
            uVar8 = 1;
            goto LAB_102081b0;
          }
          if (uVar8 == 2) {
            iVar7 = gx8002_uart_body_probe(param_1,puVar10,DAT_102082a4,&uStack_30);
            if (iVar7 == 1) {
LAB_102081f0:
              puVar3[0x5c] = 0;
              *(char *)(puVar3 + 0xc) = (char)param_1;
              puVar3[0xd] = (uint)(ushort)puVar3[9] +
                            (uint)(*(char *)((int)puVar3 + 0x23) != '\0') * -4;
LAB_1020828a:
              func_0x100261b8(DAT_102082a8,puVar10);
              puVar3[7] = 0;
              puVar3[0xd] = 0;
            }
            else if (iVar7 == -1) {
              uVar8 = 0;
              goto LAB_102081b0;
            }
          }
          else if (uVar8 == 3) {
            iVar7 = *(int *)(iVar1 + param_1 * 4 + 0x58c);
            uVar8 = 4 - iVar7;
            iVar9 = (uVar8 < uStack_30) * uVar8 + (uVar8 >= uStack_30) * uStack_30;
            piVar12 = *(int **)(iVar1 + 0x588);
            piVar14 = (int *)((int)piVar12 + iVar9);
            for (; piVar14 != piVar12; piVar12 = (int *)((int)piVar12 + 1)) {
              puVar3[1] = puVar3[1] >> 8 | *piVar12 << 0x18;
            }
            uStack_30 = uStack_30 - iVar9;
            iVar9 = iVar9 + iVar7;
            *(int **)(iVar1 + 0x588) = piVar14;
            if (iVar9 == 4) {
              uVar8 = puVar3[1];
              puVar3[1] = 0;
              puVar3[0xe] = uVar8;
              *(undefined4 *)(iVar13 + 0x58c) = 0;
              goto LAB_102081f0;
            }
            *(int *)(iVar13 + 0x58c) = iVar9;
          }
          else {
            uStack_30 = 0;
          }
        }
LAB_10208118:
      } while (uStack_30 != 0);
    }
    uVar4 = 0;
  }
  return uVar4;
}

