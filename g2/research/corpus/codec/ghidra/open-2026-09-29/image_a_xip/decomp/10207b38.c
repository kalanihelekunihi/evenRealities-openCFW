
undefined4 gx8002_uart_message_body(uint param_1,int param_2,uint *param_3)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  
  iVar1 = DAT_10207c44;
  iVar7 = param_1 * 4;
  iVar3 = *(int *)(DAT_10207c44 + iVar7 + 0x2f8);
  if (iVar3 == 0) {
    *(undefined4 *)(DAT_10207c44 + iVar7 + 0x300) = *(undefined4 *)(param_2 + 0x18);
  }
  iVar6 = iVar1 + iVar7;
  if (iVar3 == *(int *)(iVar6 + 0x300)) {
    *(undefined4 *)(iVar6 + 0x2f8) = 0;
    iVar1 = gx8002_channel_lookup(param_1 & 0xff);
    if (iVar1 == 0) {
      return 0xffffffff;
    }
    *(uint *)(iVar1 + 0x174) = (byte)~(*(char *)(iVar1 + 0x43) != '\0') + 2;
    gx8002_uart_transmit_start(param_1,PTR_gx8002_uart_send_callback_10207c48,0);
  }
  else {
    if (((param_2 == 0) || (param_3 == (uint *)0x0)) || (uVar2 = *param_3, uVar2 == 0)) {
      gx8002_uart_transmit_start(param_1,PTR_gx8002_uart_send_callback_10207c48,0);
      return 0xffffffff;
    }
    uVar4 = *(int *)(iVar6 + 0x300) - iVar3;
    iVar5 = (uVar4 < uVar2) * uVar4 + (uVar4 >= uVar2) * uVar2;
    gx8002_uart_write(param_1,*(int *)(param_2 + 0x10) + iVar3,iVar5);
    uVar4 = *(int *)(iVar6 + 0x2f8) + iVar5;
    uVar2 = *(uint *)(iVar6 + 0x300);
    if (uVar4 == uVar2) {
      uVar4 = 0;
    }
    *(uint *)(iVar6 + 0x2f8) = uVar4;
    *param_3 = *param_3 - iVar5;
    if (uVar4 != 0) {
      if ((*(int *)(param_2 + 0x10) + uVar4 & 0xf) != 0) {
        if (uVar4 < 0x10) {
          return 0;
        }
        if (uVar2 - uVar4 < 0x21) {
          return 0;
        }
      }
      iVar1 = iVar1 + iVar7;
      uVar2 = uVar2 - uVar4 & 0xfffffff0;
      gx8002_uart_transmit_stop(param_1);
      gx8002_uart_transmit_buffer
                (param_1,*(int *)(iVar1 + 0x2f8) + *(int *)(param_2 + 0x10),uVar2,
                 PTR_gx8002_uart_body_done_10207c4c,0);
      *(uint *)(iVar1 + 0x2f8) = uVar2 + *(int *)(iVar1 + 0x2f8);
      *param_3 = 0;
      return 0;
    }
  }
  return 1;
}

