
undefined4 gx8002_uart_body_probe(uint param_1,int param_2,int *param_3,uint *param_4)

{
  char cVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  undefined1 *puVar8;
  undefined4 uVar9;
  int iVar10;
  uint uVar11;
  int iVar12;
  undefined1 *puVar13;
  int iVar14;
  int iVar15;
  
  iVar2 = gx8002_channel_lookup(param_1 & 0xff);
  iVar10 = DAT_10207ecc;
  iVar3 = DAT_10207ecc + param_1 * 4;
  uVar7 = (uint)*(ushort *)(param_2 + 8) + (uint)(*(char *)(param_2 + 7) != '\0') * -4;
  uVar6 = *(uint *)(iVar3 + 0x308);
  puVar8 = (undefined1 *)*param_3;
  if (uVar7 == uVar6) {
    *(undefined4 *)(iVar3 + 0x308) = 0;
    gx8002_uart_receive_start
              (*(undefined4 *)(iVar2 + 8),PTR_gx8002_uart_receive_callback_10207ed0,0);
    if (*(char *)(param_2 + 7) == '\0') {
      *(undefined4 *)(iVar2 + 0x170) = 0;
      *(char *)(iVar2 + 0x30) = (char)param_1;
      *(uint *)(iVar2 + 0x34) =
           (uint)*(ushort *)(iVar2 + 0x24) + (uint)(*(char *)(iVar2 + 0x23) != '\0') * -4;
      func_0x100261b8(DAT_10207ed4,iVar2 + 0x1c);
      *(undefined4 *)(iVar2 + 0x1c) = 0;
      *(undefined4 *)(iVar2 + 0x34) = 0;
      return 0;
    }
LAB_10207e66:
    uVar9 = 0;
    *(undefined4 *)(iVar2 + 0x170) = 3;
  }
  else {
    if (uVar6 == 0) {
      iVar3 = DAT_10207ecc + 0x310;
      iVar12 = 0x10;
      iVar4 = 0;
      iVar14 = 0;
      do {
        iVar15 = iVar3 + iVar14;
        iVar14 = iVar14 + 0x1c;
        if (*(uint *)(iVar15 + 4) == (uint)*(ushort *)(param_2 + 4)) {
          iVar14 = iVar3 + iVar4 * 0x1c;
          if (uVar7 <= *(uint *)(iVar14 + 0xc)) {
            if (*(uint *)(iVar14 + 0xc) < (uint)*(ushort *)(param_2 + 8) + *(int *)(iVar14 + 0x10))
            {
              *(undefined4 *)(iVar14 + 0x10) = 0;
            }
            iVar3 = iVar3 + iVar4 * 0x1c;
            if (*(int *)(iVar3 + 8) != 0) {
              iVar4 = *(int *)(iVar3 + 0x10);
              *(int *)(param_2 + 0x10) = *(int *)(iVar3 + 8) + iVar4;
              *(uint *)(iVar3 + 0x10) = iVar4 + uVar7;
              goto LAB_10207dfa;
            }
          }
          break;
        }
        iVar4 = iVar4 + 1;
        iVar12 = iVar12 + -1;
      } while (iVar12 != 0);
      *(undefined4 *)(param_2 + 0x10) = 0;
      *(undefined4 *)(param_2 + 0x18) = 0;
    }
    else {
LAB_10207dfa:
      if (((*param_3 != 0) && (param_4 != (uint *)0x0)) && (uVar11 = *param_4, uVar11 != 0)) {
        uVar5 = uVar7 - uVar6;
        iVar3 = (uVar5 < uVar11) * uVar5 + (uVar5 >= uVar11) * uVar11;
        puVar13 = puVar8 + iVar3;
        iVar4 = uVar6 - (int)puVar8;
        for (; puVar13 != puVar8; puVar8 = puVar8 + 1) {
          puVar8[iVar4 + *(int *)(param_2 + 0x10)] = *puVar8;
        }
        iVar10 = iVar10 + param_1 * 4;
        uVar6 = uVar6 + iVar3;
        *(uint *)(iVar10 + 0x308) = uVar6;
        *param_4 = *param_4 - iVar3;
        if (uVar7 != uVar6) {
          if (uVar7 - uVar6 < 0x21) {
            return 0;
          }
          uVar11 = *(uint *)(param_2 + 0x10) + uVar6;
          if (uVar11 <= (*(uint *)(param_2 + 0x10) & 0xfffffff0) + 0x10) {
            return 0;
          }
          uVar6 = uVar7 - uVar6 & 0xfffffff0;
          gx8002_uart_receive_stop(param_1);
          gx8002_uart_receive_buffer
                    (param_1,uVar11,uVar6,PTR_gx8002_uart_receive_body_done_10207ed8,0);
          *param_4 = 0;
          iVar2 = DAT_10207edc;
          *(uint *)(iVar10 + 0x308) = uVar6 + *(int *)(iVar10 + 0x308);
          *param_3 = iVar2;
          return 0;
        }
        cVar1 = *(char *)(param_2 + 7);
        *param_3 = iVar3 + *param_3;
        *(undefined4 *)(iVar10 + 0x308) = 0;
        if (cVar1 == '\0') {
          return 1;
        }
        goto LAB_10207e66;
      }
      gx8002_uart_receive_start
                (*(undefined4 *)(iVar2 + 8),PTR_gx8002_uart_receive_callback_10207ed0,0);
    }
    uVar9 = 0xffffffff;
  }
  return uVar9;
}

