
void nvdbMacUpdate(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  undefined2 uVar2;
  
  puVar1 = DAT_005da060;
  FUN_00439be4(DAT_005da060 + 1,param_1,6,param_4,param_4);
  *puVar1 = 1;
  uVar2 = FUN_0049acd4(puVar1,8,0);
  *(undefined2 *)(puVar1 + 8) = uVar2;
  SVC_NvdbWrite(DAT_005da078,puVar1,10);
  return;
}

