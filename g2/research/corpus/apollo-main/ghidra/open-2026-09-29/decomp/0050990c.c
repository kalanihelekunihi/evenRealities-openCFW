
void nvdbSensorCaldataUpdate
               (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
               undefined4 param_5)

{
  undefined1 *puVar1;
  undefined2 uVar2;
  undefined4 uVar3;
  
  puVar1 = DAT_00509afc;
  *DAT_00509afc = 1;
  FUN_00439be4(puVar1 + 4,param_1,0xc,param_4,param_4);
  FUN_00439be4(puVar1 + 0x10,param_2,0xc);
  FUN_00439be4(puVar1 + 0x1c,param_3,0x10);
  uVar3 = FUN_00439be4(puVar1 + 0x2c,param_4,0x10);
  *(undefined4 *)(puVar1 + 0x3c) = uVar3;
  FUN_00439be4(puVar1 + 0x40,param_5,0x18);
  uVar2 = FUN_0049acd4(puVar1,0x58,0);
  *(undefined2 *)(puVar1 + 0x58) = uVar2;
  SVC_NvdbWrite(PTR_s_nvSCald_00509b14,puVar1,0x5c);
  return;
}

