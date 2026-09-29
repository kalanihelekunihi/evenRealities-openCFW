
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
_bleExactleStackInit(undefined4 param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  ushort uVar2;
  int iVar3;
  
  WsfOsInit();
  WsfTimerInit();
  uVar2 = WsfBufInit(0x2940,_DAT_004b876c,4,_DAT_004b8768,param_1,param_2,param_3,param_4);
  if (0x2940 < uVar2) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_1 = 0x30d;
      param_2 = PTR_s_Memory_pool_is_too_small_by__d_004b8770;
      FUN_0043d574(1,DAT_004b8210,DAT_004b820c,PTR_s__bleExactleStackInit_004b8774,0x30d,
                   PTR_s_Memory_pool_is_too_small_by__d_004b8770,uVar2 - 0x2940);
    }
    iVar3 = FUN_0043d0ce();
    if (-1 < iVar3 << 0x1f) {
      iVar3 = FUN_0043d0ce();
      if (-1 < iVar3 << 0x1d) goto LAB_004b7fe0;
    }
    compress_log_output(0x4400000,PTR_s__ble_comm_Memory_pool_is_too_sma_004b8778,
                        PTR_s__ble_comm_Memory_pool_is_too_sma_004b8778,uVar2 - 0x2940);
  }
LAB_004b7fe0:
  func_0x00536324();
  func_0x0053648e();
  func_0x005366cc();
  func_0x005367ca();
  uVar1 = WsfOsSetNextHandler(PTR_LAB_00536814_1_004b877c);
  func_0x005367f8(uVar1);
  uVar1 = WsfOsSetNextHandler(PTR_DmHandler_1_004b8780);
  DmDevVsInit(0);
  DmAdvInit();
  func_0x005369ea();
  DmPhyInit();
  DmConnInit();
  DmConnMasterInit();
  DmConnSlaveInit();
  DmSecInit();
  DmSecLescInit();
  DmPrivInit();
  DmHandlerInit(uVar1);
  uVar1 = WsfOsSetNextHandler(PTR_L2cSlaveHandler_1_004b8784);
  L2cSlaveHandlerInit(uVar1);
  L2cInit();
  L2cSlaveInit();
  L2cMasterInit();
  uVar1 = WsfOsSetNextHandler(PTR_AttHandler_1_004b8788);
  AttHandlerInit(uVar1);
  AttsInit();
  AttsIndInit();
  AttcInit();
  uVar1 = WsfOsSetNextHandler(PTR_SmpHandler_1_004b878c);
  SmpHandlerInit(uVar1);
  SmpiInit();
  SmpiScInit();
  SmprInit();
  SmprScInit();
  HciSetMaxRxAclLen(0xfb);
  uVar1 = WsfOsSetNextHandler(_DAT_004b8790);
  func_0x004bae6c(uVar1);
  uVar1 = WsfOsSetNextHandler(_DAT_004b8794);
  bleCommHandlerInit(uVar1);
  uVar1 = WsfOsSetNextHandler(_DAT_004b8798);
  HciDrvHandlerInit(uVar1);
  return CONCAT44(param_2,param_1);
}

