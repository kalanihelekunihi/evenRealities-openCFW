
longlong FUN_005822e6(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int *piVar1;
  undefined4 uVar2;
  undefined2 *puVar3;
  undefined2 uVar4;
  undefined4 uVar5;
  int iVar6;
  uint local_18;
  
  local_18 = 0;
  uVar5 = FUN_005848fc(param_3,1,&local_18);
  iVar6 = FUN_0044b610(uVar5,&LAB_00582444,3);
  piVar1 = DAT_00582868;
  uVar5 = DAT_00582864;
  if (iVar6 == 0) {
    FUN_0044b728(DAT_00582864,0x1a,DAT_0058286c,*DAT_00582868);
    uVar2 = DAT_00582870;
    FUN_0044b728(DAT_00582870,0x1a,DAT_00582874,*piVar1);
    *piVar1 = *piVar1 + 1;
    puVar3 = DAT_00582878;
    uVar4 = FUN_0044a43c(uVar5);
    *puVar3 = uVar4;
    uVar4 = FUN_0044a43c(uVar2);
    puVar3[0x201] = uVar4;
    FUN_00439be4(puVar3 + 1,uVar5,*puVar3);
    FUN_00439be4(puVar3 + 0x202,uVar2,puVar3[0x201]);
    *(undefined4 *)(puVar3 + 0x404) = 1;
    FUN_00596b0c(5,puVar3,0x850);
  }
  return (ulonglong)local_18 << 0x20;
}

