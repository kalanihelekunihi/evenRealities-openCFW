
undefined4 FUN_10004188(int *param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
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
  undefined4 uStack_28;
  
  iVar4 = param_1[1];
  gx8002_dcache_invalid_range(param_1[0x18],param_1[0x19]);
  iVar1 = gx8002_backup_dma_select();
  if (iVar1 < 0) {
LAB_10004214:
    uVar2 = 0xffffffff;
  }
  else {
    iVar3 = param_1[0xd];
    param_1[0x1a] = iVar1;
    uStack_4c = 1;
    uStack_44 = 1;
    uStack_54 = 0;
    uStack_40 = 0;
    uStack_50 = FUN_10004078(iVar3,param_1 + 0xe);
    if (*param_1 == 0) {
      uStack_48 = 6;
    }
    else {
      if (*param_1 != 1) goto LAB_10004214;
      uStack_48 = 4;
    }
    uStack_38 = 0;
    uStack_2c = 0;
    uStack_30 = 0;
    uStack_3c = FUN_10004078(iVar3,param_1 + 0xe,0);
    uStack_28 = 2;
    uStack_34 = 0;
    gx8002_dma_callback(iVar1,PTR_gx8002_uart_receive_complete_1000421c,param_1);
    gx8002_dma_transfer(param_2,iVar4,param_3,iVar1,&uStack_54);
    uVar2 = 0;
  }
  return uVar2;
}

