
undefined8 FUN_00544f6c(int param_1,undefined4 param_2,int param_3,int param_4)

{
  byte bVar1;
  char cVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  
  bVar1 = 0;
  if (param_3 == 0) {
    bVar1 = FUN_005448b4(param_1,param_2,0,1);
  }
  else {
    uVar3 = FUN_0044a43c(param_2);
    iVar4 = FUN_00544b78(param_1,param_1 + 0x8c,uVar3,param_4);
    if (iVar4 == -1) {
      uVar5 = 7;
      goto LAB_00545036;
    }
    cVar2 = FUN_0054449a(param_1,param_2,param_1 + 0x34);
    if (cVar2 != '\0') {
      bVar1 = FUN_005448b4(param_1,param_2,param_1 + 0x34,0);
    }
    if (bVar1 == 0) {
      bVar1 = FUN_00544d60(param_1,param_1 + 0x8c,param_2,param_3);
    }
    if ((cVar2 != '\0') && (bVar1 == 0)) {
      bVar1 = FUN_005448b4(param_1,param_2,param_1 + 0x34,1);
    }
    if (*(char *)(param_1 + 0x30) != '\0') {
      iVar4 = FUN_0044a43c(param_2);
      FUN_0044a43c(param_2);
      FUN_00544c78(param_1,param_4 + iVar4 + 0x18);
    }
  }
  uVar5 = (uint)bVar1;
LAB_00545036:
  return CONCAT44(param_4,uVar5);
}

