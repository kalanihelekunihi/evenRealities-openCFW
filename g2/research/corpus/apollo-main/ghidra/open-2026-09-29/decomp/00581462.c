
undefined8 FUN_00581462(int param_1,int param_2,char *param_3,undefined4 param_4)

{
  undefined1 uVar1;
  uint uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  uint uVar5;
  char *local_20;
  undefined4 uStack_1c;
  
  local_20 = param_3;
  uStack_1c = param_4;
  uVar2 = FUN_0044a43c(param_1);
  if ((int)(uVar2 << 0x1f) < 0) {
    FUN_00595a34(DAT_00581704);
    uVar3 = 0xffffffff;
  }
  else {
    FUN_0043c0e4(&uStack_1c,3,0);
    uVar3 = 0;
    for (uVar5 = 0; uVar5 < uVar2; uVar5 = uVar5 + 2) {
      uVar4 = FUN_0044b5a0(&uStack_1c,param_1 + uVar5,2);
      uVar1 = FUN_00595a2e(uVar4,&local_20,0x10);
      if (*local_20 != '\0') {
        FUN_00595a34(DAT_00581708,uVar5);
        uVar3 = 0xffffffff;
        break;
      }
      *(undefined1 *)(param_2 + (uVar5 >> 1)) = uVar1;
    }
  }
  return CONCAT44(local_20,uVar3);
}

