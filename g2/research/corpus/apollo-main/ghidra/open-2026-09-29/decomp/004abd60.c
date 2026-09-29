
undefined4 CB_BLE_STATUS_Notify(undefined4 param_1,undefined4 param_2)

{
  undefined4 uStack_8;
  
  uStack_8 = param_2;
  CALLBACK_MGR_Notify(DAT_004abd74,param_1,&uStack_8);
  return uStack_8;
}

