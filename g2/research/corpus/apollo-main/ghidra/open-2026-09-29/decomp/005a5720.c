
undefined4
atInfoHandler(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined1 *puVar2;
  
  at_core_output(PTR_s_Product_name____s__005a57b8,PTR_LAB_005a57b4,param_3,param_4,param_1,param_2,
                 param_3,param_4);
  uVar1 = func_0x0057e6cc();
  at_core_output(PTR_s_Hardware_version____s__005a57bc,uVar1);
  at_core_output(PTR_s_Software_version____s__005a57c4,PTR_s_2_2_6_10_005a57c0);
  uVar1 = func_0x0057e702();
  at_core_output(PTR_s_Codec_version____s__005a57c8,uVar1);
  uVar1 = semantic_TouchLogCurrentVersion();
  at_core_output(PTR_s_Touch_version____s__005a57cc,uVar1);
  at_core_output(PTR_s_Compile_time____s__s__005a57d8,PTR_s_Jul_6_2026_005a57d4,
                 PTR_s_21_37_47_005a57d0);
  uVar1 = SVC_NvdbReadSysData(0);
  at_core_output(PTR_s_Product_SN____s__005a57dc,uVar1);
  puVar2 = (undefined1 *)APP_BleAddressGet();
  uVar1 = APP_BleNameGet();
  at_core_output(PTR_s_BLE_NAME____s__005a57e0,uVar1);
  at_core_output(PTR_s_BLE_ADDR____02X__02X__02X__02X___005a57e4,puVar2[5],puVar2[4],puVar2[3],
                 puVar2[2],puVar2[1],*puVar2);
  at_core_output(PTR_s_INFO_OK_005a57e8);
  return 1;
}

