
undefined8 FUN_00590b92(uint *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  int iVar2;
  uint *puVar3;
  uint uVar4;
  undefined1 uVar5;
  
  uVar4 = param_1[1];
  if (uVar4 == 0) {
    uVar5 = 0x1d;
  }
  else {
    uVar5 = 0x1e;
  }
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_00590d38)) {
    iVar2 = 2;
  }
  else if ((int)(*param_1 << 6) < 0) {
    iVar2 = 0;
  }
  else {
    iVar2 = FUN_004c44bc(4,uVar5);
    if (iVar2 == 0) {
      if ((char)param_1[0x18] == '\0') {
        FUN_0058fdbc(uVar4,0x217);
        iVar2 = DAT_00590d34;
        puVar3 = (uint *)(DAT_00590d34 + uVar4 * 0x1000 + 0x100);
        *puVar3 = *puVar3 & 0xfffffffe;
        puVar3 = (uint *)(iVar2 + uVar4 * 0x1000 + 0x100);
        *puVar3 = *puVar3 & 0xffffefff;
      }
      else {
        uVar1 = FUN_0058fd1c(param_1[0x17]);
        iVar2 = FUN_004c44bc(uVar1,uVar5);
        if (iVar2 != 0) {
          FUN_004c4530(4,uVar5);
          goto LAB_00590c60;
        }
        FUN_0058fdbc(uVar4,param_1[0x17]);
        iVar2 = DAT_00590d34;
        puVar3 = (uint *)(DAT_00590d34 + uVar4 * 0x1000 + 0x100);
        *puVar3 = *puVar3 | 1;
        puVar3 = (uint *)(iVar2 + uVar4 * 0x1000 + 0x100);
        *puVar3 = *puVar3 | 0x1000;
      }
      *param_1 = *param_1 | 0x2000000;
      iVar2 = 0;
    }
  }
LAB_00590c60:
  return CONCAT44(param_4,iVar2);
}

