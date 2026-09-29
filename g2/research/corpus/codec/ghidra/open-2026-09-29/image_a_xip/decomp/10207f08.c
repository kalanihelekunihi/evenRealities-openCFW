
undefined4 gx8002_uart_send_callback(uint param_1,uint param_2)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  uint *puVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  uint uVar11;
  int iVar12;
  uint uStack_30;
  
  iVar2 = gx8002_channel_lookup(param_1 & 0xff);
  iVar1 = DAT_10208090;
  if (iVar2 == 0) {
    uVar3 = 0xffffffff;
  }
  else {
    iVar7 = param_1 * 4;
    iVar8 = DAT_10208090 + iVar7;
    iVar6 = iVar2 + 0x3c;
    iVar9 = DAT_10208090 + 0x520;
    uStack_30 = param_2;
    do {
      iVar12 = *(int *)(iVar2 + 0x174);
      if (iVar12 == 1) {
        iVar12 = gx8002_uart_message_body(param_1,iVar6,&uStack_30);
        if (iVar12 == 1) {
          iVar12 = (byte)~(*(char *)(iVar2 + 0x43) != '\0') + 2;
LAB_10207fac:
          *(int *)(iVar2 + 0x174) = iVar12;
        }
      }
      else if (iVar12 == 0) {
        iVar4 = iVar1 + iVar7;
        iVar12 = *(int *)(iVar4 + 0x510);
        uVar11 = 0xe - iVar12;
        iVar10 = (uVar11 < uStack_30) * uVar11 + (uVar11 >= uStack_30) * uStack_30;
        gx8002_uart_write(param_1,iVar12 + iVar6,iVar10);
        iVar12 = iVar10 + *(int *)(iVar4 + 0x510);
        if (iVar12 == 0xe) {
          iVar12 = 0;
        }
        uStack_30 = uStack_30 - iVar10;
        *(int *)(iVar8 + 0x510) = iVar12;
        if (iVar12 == 0) {
          iVar12 = 3;
          if (*(short *)(iVar2 + 0x44) != 0) {
            iVar12 = 1;
          }
          goto LAB_10207fac;
        }
      }
      else if (iVar12 == 2) {
        iVar12 = iVar1 + iVar7;
        if (*(int *)(iVar12 + 0x518) == 0) {
          uVar3 = crc32(0,*(undefined4 *)(iVar2 + 0x4c),*(undefined4 *)(iVar2 + 0x54));
          *(undefined4 *)(iVar12 + 0x520) = uVar3;
        }
        uVar11 = 4 - *(int *)(iVar8 + 0x518);
        iVar4 = (uVar11 < uStack_30) * uVar11 + (uVar11 >= uStack_30) * uStack_30;
        gx8002_uart_write(param_1,*(int *)(iVar8 + 0x518) + iVar7 + iVar9,iVar4);
        iVar12 = iVar4 + *(int *)(iVar8 + 0x518);
        if (iVar12 == 4) {
          iVar12 = 0;
        }
        uStack_30 = uStack_30 - iVar4;
        *(int *)(iVar8 + 0x518) = iVar12;
        if (iVar12 == 0) {
          iVar12 = 3;
          goto LAB_10207fac;
        }
      }
      else if (iVar12 == 3) {
        iVar12 = gx8002_channel_lookup(*(undefined1 *)(iVar2 + 0x50));
        if (iVar12 != 0) {
          gx8002_power_unlock(*(undefined4 *)(iVar12 + 0x178));
          iVar4 = 0;
          iVar12 = 6;
          puVar5 = DAT_10208094;
          do {
            if ((puVar5[1] == (uint)*(ushort *)(iVar2 + 0x40)) &&
               (*puVar5 == (uint)*(byte *)(iVar2 + 0x50))) {
              (*(code *)(DAT_10208094[iVar4 * 4 + 2] & 0xfffffffe))
                        (iVar6,DAT_10208094[iVar4 * 4 + 3]);
              break;
            }
            iVar4 = iVar4 + 1;
            puVar5 = puVar5 + 4;
            iVar12 = iVar12 + -1;
          } while (iVar12 != 0);
        }
        iVar12 = gx8002_uart_message_start(param_1 & 0xff);
        if (iVar12 == -1) break;
      }
    } while (uStack_30 != 0);
    uVar3 = 0;
  }
  return uVar3;
}

