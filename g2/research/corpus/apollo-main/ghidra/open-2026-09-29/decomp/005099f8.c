
undefined4 nvdbSensorCaldataAgRead(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = DAT_00509b30;
  uVar2 = SVC_NvdbRead(DAT_00509b34,DAT_00509b30,0x44);
  _nvdbCheckSensorCaldata();
  FUN_00439be4(param_1,iVar1 + 4,0xc);
  FUN_00439be4(param_2,iVar1 + 0x10,0xc);
  FUN_00439be4(param_3,iVar1 + 0x1c,0x24);
  return uVar2;
}

