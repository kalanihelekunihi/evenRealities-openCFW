
undefined4 gx8002_uart_transmit_dma_entry(int *param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 local_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  
  iVar3 = param_1[1];
  func_0x10025664(param_2,param_3);
  iVar1 = gx8002_dma_select();
  if (iVar1 < 0) {
    uVar2 = 0xffffffff;
  }
  else {
    param_1[0x1f] = iVar1;
    local_54 = 0;
    uStack_4c = 0;
    uStack_40 = 0;
    uStack_44 = 0;
    uStack_50 = dw_uart_get_dma_burst_size(param_1,1);
    uStack_48 = 0;
    uStack_38 = 1;
    uStack_2c = 0;
    uStack_30 = 1;
    uStack_3c = dw_uart_get_dma_burst_size(param_1,1);
    if (*param_1 == 0) {
      uStack_34 = 7;
    }
    else if (*param_1 == 1) {
      uStack_34 = 5;
    }
    uStack_28 = 1;
    gx8002_dma_callback(iVar1,PTR_gx8002_uart_transmit_complete_1020318c,param_1);
    gx8002_dma_transfer(iVar3,param_2,param_3,iVar1,&local_54);
    uVar2 = 0;
  }
  return uVar2;
}

