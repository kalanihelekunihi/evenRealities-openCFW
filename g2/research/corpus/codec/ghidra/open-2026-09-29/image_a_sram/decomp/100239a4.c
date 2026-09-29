
int gx8002_flash_write_protect_set(uint param_1,undefined4 *param_2)

{
  byte bVar1;
  byte bVar2;
  int iVar3;
  int *piVar4;
  undefined4 *puVar5;
  int iVar6;
  byte *pbVar7;
  byte bVar8;
  byte bVar9;
  byte bVar10;
  uint uVar11;
  byte local_28;
  byte bStack_27;
  undefined4 uStack_24;
  
  iVar3 = DAT_10023a6c;
  local_28 = 0;
  bStack_27 = 0;
  iVar6 = *(int *)(DAT_10023a6c + 0xc);
  bVar8 = 0;
  piVar4 = *(int **)(iVar6 + 0x10);
  *param_2 = 0;
  if ((piVar4 == (int *)0x0) || (*piVar4 == 0)) {
    iVar3 = -(uint)(param_1 != 0);
  }
  else {
    uVar11 = *(uint *)(iVar6 + 4);
    gx8002_flash_wait_ready();
    bVar10 = 0;
    puVar5 = *(undefined4 **)(*(int *)(iVar3 + 0xc) + 0x10);
    bVar9 = 0;
    bVar2 = 0;
    iVar3 = 0;
    for (pbVar7 = (byte *)*puVar5; (iVar3 != puVar5[1] && (*(uint *)(pbVar7 + 4) <= param_1));
        pbVar7 = pbVar7 + 8) {
      iVar3 = iVar3 + 1;
      bVar2 = *pbVar7;
      bVar9 = pbVar7[2];
      bVar10 = pbVar7[1];
      bVar8 = pbVar7[3];
    }
    uVar11 = uVar11 >> 0x10;
    if ((uVar11 == 0x5e) || (uVar11 == 0x85)) {
      bVar1 = gx8002_flash_read_status();
      local_28 = bVar2 | bVar1 & ~bVar10;
      bVar2 = gx8002_flash_read_status2();
      bStack_27 = bVar2 & ~bVar8 | bVar9;
      gx8002_flash_wait_ready();
      gx8002_flash_write_enable();
      gx8002_flash_command_write(1,&local_28,2);
      gx8002_flash_wait_ready();
      iVar3 = gx8002_flash_write_protect_status(&uStack_24);
      if (iVar3 != -1) {
        *param_2 = uStack_24;
        iVar3 = 0;
      }
    }
    else {
      iVar3 = -1;
    }
  }
  return iVar3;
}

