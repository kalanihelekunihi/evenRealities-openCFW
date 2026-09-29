
undefined8 FUN_005cf9e8(undefined4 *param_1,int param_2,int param_3,int param_4)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  int *piVar4;
  byte *pbVar5;
  int iVar6;
  int local_30;
  int local_2c;
  int local_28;
  
  piVar4 = (int *)param_1[1];
  local_30 = param_2;
  if (param_3 < 6) {
    local_2c = param_3;
    local_28 = param_4;
    for (iVar2 = 0; iVar2 < param_3; iVar2 = iVar2 + 1) {
      pbVar5 = (byte *)(param_2 + iVar2 * 8);
      if (*pbVar5 == 0) {
        local_30 = FUN_005cf99a(piVar4);
      }
      else {
        local_30 = FUN_005cf938(piVar4);
      }
      if (local_30 == 0) break;
      iVar6 = (*piVar4 - local_30) + -1;
      bVar1 = *pbVar5;
      if (bVar1 == 0) {
LAB_005cfa62:
        uVar3 = ft_mem_qalloc(*param_1,*piVar4 - local_30,&local_2c);
        *(undefined4 *)(pbVar5 + 4) = uVar3;
        if (local_2c == 0) {
          local_28 = local_30;
          FUN_00439be4(*(undefined4 *)(pbVar5 + 4),local_30,iVar6);
          *(undefined1 *)(*(int *)(pbVar5 + 4) + iVar6) = 0;
        }
      }
      else if (bVar1 == 2) {
        uVar3 = FUN_005d01de(&local_30,local_30 + iVar6,0);
        *(undefined4 *)(pbVar5 + 4) = uVar3;
      }
      else {
        if (bVar1 < 2) goto LAB_005cfa62;
        if (bVar1 == 4) {
          if ((iVar6 == 4) && (iVar6 = FUN_0044b610(local_30,DAT_005d0570,4), iVar6 == 0)) {
            bVar1 = 1;
          }
          else {
            bVar1 = 0;
          }
          pbVar5[4] = bVar1;
        }
        else if (bVar1 < 4) {
          uVar3 = FUN_005d018a(&local_30,local_30 + iVar6);
          *(undefined4 *)(pbVar5 + 4) = uVar3;
        }
        else if (bVar1 == 5) {
          if (param_1[3] == 0) {
            pbVar5[4] = 0;
            pbVar5[5] = 0;
            pbVar5[6] = 0;
            pbVar5[7] = 0;
          }
          else {
            uVar3 = (*(code *)param_1[3])(local_30,iVar6,param_1[4]);
            *(undefined4 *)(pbVar5 + 4) = uVar3;
          }
        }
      }
    }
  }
  else {
    iVar2 = 0;
  }
  return CONCAT44(local_30,iVar2);
}

