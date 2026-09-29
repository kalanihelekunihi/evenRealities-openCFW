
undefined4 gx8002_uart_receive_dma(int *param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 local_50;
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
  undefined4 uStack_24;
  
  iVar3 = param_1[1];
  func_0x10025608(param_1[0x18],param_1[0x19]);
  iVar1 = gx8002_dma_select();
  if (iVar1 < 0) {
LAB_102031b0:
    uVar2 = 0xffffffff;
  }
  else {
    param_1[0x1a] = iVar1;
    uStack_48 = 1;
    uStack_40 = 1;
    local_50 = 0;
    uStack_3c = 0;
    uStack_4c = dw_uart_get_dma_burst_size(param_1);
    if (*param_1 == 0) {
      uStack_44 = 6;
    }
    else {
      if (*param_1 != 1) goto LAB_102031b0;
      uStack_44 = 4;
    }
    uVar2 = 0;
    uStack_34 = 0;
    uStack_28 = 0;
    uStack_2c = 0;
    uStack_38 = dw_uart_get_dma_burst_size(param_1,0);
    uStack_24 = 2;
    uStack_30 = 0;
    gx8002_dma_callback(iVar1,PTR_gx8002_uart_receive_complete_10203218,param_1);
    gx8002_dma_transfer(param_2,iVar3,param_3,iVar1,&local_50);
  }
  return uVar2;
}

