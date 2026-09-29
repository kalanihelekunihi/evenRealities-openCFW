
undefined8
task_vote_acquire_for_handle(int param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  bool bVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  byte bVar5;
  undefined4 local_10;
  
  iVar2 = DAT_0046d878;
  if ((*(char *)(DAT_0046d878 + 0x104) == '\0') || (param_1 == 0)) {
    uVar3 = 0;
    local_10 = param_4;
  }
  else {
    local_10 = FUN_00473940(0);
    iVar4 = task_vote_find_slot(param_1);
    if (iVar4 < 0) {
      iVar4 = task_vote_find_free_slot();
      if (iVar4 < 0) {
        bVar5 = 0;
      }
      else {
        *(int *)(iVar2 + iVar4 * 8) = param_1;
        *(undefined1 *)(iVar2 + iVar4 * 8 + 4) = 1;
        *(int *)(iVar2 + 0x100) = *(int *)(iVar2 + 0x100) + 1;
        bVar5 = 1;
      }
    }
    else if (*(char *)(iVar2 + iVar4 * 8 + 4) == '\0') {
      *(undefined1 *)(iVar2 + iVar4 * 8 + 4) = 1;
      *(int *)(iVar2 + 0x100) = *(int *)(iVar2 + 0x100) + 1;
      bVar5 = 1;
    }
    else {
      bVar5 = 0;
    }
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_10 & 1) == 1);
    }
    uVar3 = (uint)bVar5;
  }
  return CONCAT44(local_10,uVar3);
}

