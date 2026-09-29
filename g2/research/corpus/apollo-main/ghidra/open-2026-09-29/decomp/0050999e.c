
void nvdbSensorCaldataAgUpdate(int param_1,int param_2,int param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  undefined2 uVar2;
  
  puVar1 = DAT_00509b30;
  *DAT_00509b30 = 1;
  if (param_1 != 0) {
    FUN_00439be4(puVar1 + 4,param_1,0xc,param_4,param_4);
  }
  if (param_2 != 0) {
    FUN_00439be4(puVar1 + 0x10,param_2,0xc);
  }
  if (param_3 != 0) {
    FUN_00439be4(puVar1 + 0x1c,param_3,0x24);
  }
  uVar2 = FUN_0049acd4(puVar1,0x40,0);
  *(undefined2 *)(puVar1 + 0x40) = uVar2;
  SVC_NvdbWrite(DAT_00509b34,puVar1,0x44);
  return;
}

