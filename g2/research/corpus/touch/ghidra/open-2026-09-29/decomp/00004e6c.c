
void touch_application_1b6c_update(int param_1,int param_2)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  bool bVar6;
  undefined4 local_2c;
  
  iVar2 = *(int *)(param_2 + 0xc) + param_1 * 0x90;
  uVar1 = (uint)*(ushort *)(iVar2 + 0x74);
  if (*(char *)(iVar2 + 0x7b) != '\a') {
    local_2c = 0;
    bVar6 = false;
    while (!bVar6) {
      for (uVar3 = 0; uVar3 < *(ushort *)(iVar2 + 0x38); uVar3 = uVar3 + 1) {
        iVar5 = *(int *)(iVar2 + 4) + uVar3 * 10;
        iVar4 = *(int *)(iVar2 + 0x1c) + uVar3 * (uVar1 & 0xf) * 2;
        if ((int)(uVar1 << 0x1b) < 0) {
          touch_record_1b58_replicate2(iVar2,iVar5,iVar4);
          iVar4 = iVar4 + 4;
        }
        if ((int)(uVar1 << 0x18) < 0) {
          if ((*(ushort *)(iVar2 + 0x74) & 0x300) == 0x200) {
            local_2c = *(int *)(iVar2 + 0x20) + uVar3;
          }
          touch_record_1b36_copy_gate(iVar2,iVar5,iVar4,local_2c);
          iVar4 = iVar4 + 2;
        }
        if ((int)(uVar1 << 0x15) < 0) {
          touch_record_1b60_replicate3(iVar2,iVar5,iVar4);
        }
      }
      bVar6 = true;
    }
  }
  return;
}

