
undefined4 FUN_100040e8(int *param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  undefined4 local_58;
  undefined4 uStack_54;
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
  
  iVar3 = param_1[1];
  gx8002_dcache_clean_range(param_2,param_3);
  iVar1 = gx8002_backup_dma_select();
  if (iVar1 < 0) {
    uVar2 = 0xffffffff;
  }
  else {
    iVar4 = param_1[0xd];
    param_1[0x1f] = iVar1;
    local_58 = 0;
    uStack_50 = 0;
    uStack_44 = 0;
    uStack_48 = 0;
    uStack_54 = FUN_10004078(iVar4,param_1 + 0xe,1);
    uStack_4c = 0;
    uStack_3c = 1;
    uStack_30 = 0;
    uStack_34 = 1;
    uStack_40 = FUN_10004078(iVar4,param_1 + 0xe);
    if (*param_1 == 0) {
      uStack_38 = 7;
    }
    else if (*param_1 == 1) {
      uStack_38 = 5;
    }
    uStack_2c = 1;
    gx8002_dma_callback(iVar1,PTR_gx8002_uart_transmit_complete_10004184,param_1);
    gx8002_dma_transfer(iVar3,param_2,param_3,iVar1,&local_58);
    uVar2 = 0;
  }
  return uVar2;
}

