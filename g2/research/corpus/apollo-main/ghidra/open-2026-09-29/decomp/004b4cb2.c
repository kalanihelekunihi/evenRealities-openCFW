
undefined8 HciVscSetRfPowerLevelEx(undefined4 param_1)

{
  bool bVar1;
  undefined4 local_8;
  
  local_8._0_1_ = (char)param_1;
  bVar1 = (int)(char)local_8 + 0x1bU < 0x22;
  local_8 = param_1;
  if (bVar1) {
    HciVendorSpecificCmd(0xfcc4,1,&local_8);
  }
  return CONCAT44(local_8,(uint)bVar1);
}

