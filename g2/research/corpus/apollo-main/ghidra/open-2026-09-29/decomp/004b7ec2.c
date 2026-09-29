
void bleStackRegister(void)

{
  undefined *puVar1;
  
  puVar1 = PTR_bleDmCback_1_004b8734;
  DmRegister(PTR_bleDmCback_1_004b8734);
  DmConnRegister(3,puVar1);
  AttRegister(PTR_bleAttCback_1_004b8738);
  AttConnRegister(PTR_LAB_005345aa_1_004b873c);
  AttsCccRegister(6,PTR_DAT_004b8744,PTR_bleCccCback_1_004b8740);
  func_0x00532e7c(PTR_APP_BleServerDiscCback_1_004b8748);
  func_0x0052dc1c(PTR_GattReadCback_1_004b8750,PTR_GattWriteCback_1_004b874c);
  func_0x0052dbf0();
  func_0x0053618c();
  func_0x005361c6(0,PTR_APP_EvenOtaWriteCback_1_004b8754);
  func_0x005361bc();
  func_0x005361de(0,PTR_eusWriteCallback_1_004b8758);
  func_0x005361d4();
  func_0x005361f6(0,PTR_essWriteCallback_1_004b875c);
  func_0x005361ec();
  func_0x0053620e(0,PTR_efsWriteCallback_1_004b8760);
  func_0x00536204();
  func_0x00536226(0,PTR_nusWriteCallback_1_004b8764);
  func_0x0053621c();
  GattSetSvcChangedIdx(0);
  return;
}

