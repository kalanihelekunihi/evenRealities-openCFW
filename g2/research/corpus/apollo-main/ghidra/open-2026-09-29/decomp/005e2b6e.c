
undefined4 smpScActAuthSelect(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  ushort uVar2;
  int iVar3;
  undefined4 local_10;
  
  iVar3 = *(int *)(param_2 + 4);
  local_10 = param_4;
  WStrReverseCpy(*(undefined4 *)(*(int *)(param_1 + 0x48) + 8),iVar3 + 9,0x20);
  WStrReverseCpy(*(int *)(*(int *)(param_1 + 0x48) + 8) + 0x20,iVar3 + 0x29,0x20);
  uVar2 = (ushort)*(byte *)(param_1 + 0x3d);
  bVar1 = *(byte *)(*(int *)(param_1 + 0x48) + 1);
  if (bVar1 == 1) {
LAB_005e2bb0:
    local_10._0_3_ = CONCAT12(0x13,uVar2);
  }
  else {
    if (bVar1 != 0) {
      if (bVar1 == 3) {
        local_10._0_3_ = CONCAT12(0x14,uVar2);
        goto LAB_005e2bd4;
      }
      if (bVar1 < 3) {
        local_10._0_3_ = CONCAT12(0x15,uVar2);
        goto LAB_005e2bd4;
      }
      if (bVar1 == 4) goto LAB_005e2bb0;
    }
    local_10._0_3_ = CONCAT12(3,uVar2);
    local_10 = CONCAT13(8,(undefined3)local_10);
  }
LAB_005e2bd4:
  smpSmExecute(param_1,&local_10);
  return local_10;
}

