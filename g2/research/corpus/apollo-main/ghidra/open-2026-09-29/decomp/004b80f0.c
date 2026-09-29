
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 appBleStart(void)

{
  undefined4 unaff_r7;
  
  vendorCcbInitLike();
  HciDrvRadioShutdown();
  FUN_00491102(100);
  HciDrvRadioBoot(0);
  _bleExactleStackInit();
  bleStackRegister();
  DmDevReset();
  fw_event_loop_push_delayed(_DAT_004b87a0,0,10000);
  return unaff_r7;
}

