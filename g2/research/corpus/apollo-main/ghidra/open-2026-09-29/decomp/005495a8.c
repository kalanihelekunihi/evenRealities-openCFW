
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_005495a8(void)

{
  undefined4 *puVar1;
  char *pcVar2;
  undefined1 *puVar3;
  undefined4 uVar4;
  
  puVar1 = _DAT_00549bb0;
  osMutexAcquire(*_DAT_00549bb0,0xffffffff);
  puVar3 = _DAT_00549bb8;
  pcVar2 = _DAT_00549bb4;
  if (*_DAT_00549bb4 == '\x01') {
    *_DAT_00549bb8 = 1;
    *(undefined4 *)(puVar3 + 4) = *(undefined4 *)(pcVar2 + 4);
    FUN_0043c0e4(puVar3 + 8,0x40,0);
    uVar4 = FUN_0044a43c(pcVar2 + 8);
    FUN_00439be4(puVar3 + 8,pcVar2 + 8,uVar4);
    FUN_0043c0e4(puVar3 + 0x48,0x40,0);
    uVar4 = FUN_0044a43c(pcVar2 + 0x48);
    FUN_00439be4(puVar3 + 0x48,pcVar2 + 0x48,uVar4);
    FUN_0043c0e4(puVar3 + 0x88,0x40,0);
    uVar4 = FUN_0044a43c(pcVar2 + 0x88);
    FUN_00439be4(puVar3 + 0x88,pcVar2 + 0x88,uVar4);
    FUN_0043c0e4(puVar3 + 200,0x40,0);
    uVar4 = FUN_0044a43c(pcVar2 + 200);
    FUN_00439be4(puVar3 + 200,pcVar2 + 200,uVar4);
    FUN_0043c0e4(puVar3 + 0x108,0x40,0);
    uVar4 = FUN_0044a43c(pcVar2 + 0x108);
    FUN_00439be4(puVar3 + 0x108,pcVar2 + 0x108,uVar4);
    FUN_0043c0e4(puVar3 + 0x148,0x40,0);
    uVar4 = FUN_0044a43c(pcVar2 + 0x148);
    FUN_00439be4(puVar3 + 0x148,pcVar2 + 0x148,uVar4);
    *(undefined4 *)(puVar3 + 0x188) = *(undefined4 *)(pcVar2 + 0x188);
    FUN_0043c0e4(pcVar2,0x18c,0);
  }
  else {
    *_DAT_00549bb8 = 0;
  }
  osMutexRelease(*puVar1);
  return;
}

