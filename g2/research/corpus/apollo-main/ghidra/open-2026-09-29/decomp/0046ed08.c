
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 APP_BleNameGet(void)

{
  int iVar1;
  undefined4 unaff_r5;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    unaff_r5 = 0x254;
    FUN_0043d574(4,DAT_0046ed68,DAT_0046ed64,PTR_s_APP_BleNameGet_0046f3f0,0x254,
                 PTR_s_adv_name____s_0046f3ec,_DAT_0046f3e8);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__ble_Slave_adv_name____s_0046f3f4,
                        PTR_s__ble_Slave_adv_name____s_0046f3f4,_DAT_0046f3e8);
  }
  return CONCAT44(unaff_r5,_DAT_0046f3e8);
}

