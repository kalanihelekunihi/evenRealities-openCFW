
undefined8 task_vote_blocks_deep_sleep(undefined4 param_1,undefined4 param_2,uint param_3)

{
  bool bVar1;
  int iVar2;
  uint uVar3;
  uint local_10;
  
  iVar2 = DAT_0046d878;
  if (*(char *)(DAT_0046d878 + 0x104) == '\0') {
    uVar3 = 0;
    local_10 = param_3;
  }
  else {
    local_10 = FUN_00473940();
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_10 & 1) == 1);
    }
    uVar3 = (uint)(*(int *)(iVar2 + 0x100) != 0);
  }
  return CONCAT44(local_10,uVar3);
}

