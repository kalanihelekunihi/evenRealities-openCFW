
int Cy_Flash_WriteRow(uint param_1,int param_2)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  uint local_a0;
  uint local_9c;
  undefined1 auStack_98 [132];
  
  uVar1 = Cy_Flash_GetRowNum();
  iVar2 = Cy_Flash_ValidAddr(param_1);
  iVar3 = DAT_00008e24;
  if ((iVar2 != 0) && (param_2 != 0)) {
    memcpy(auStack_98,param_2,0x80);
    iVar3 = DAT_00008e08;
    local_a0 = DAT_00008e04 | (uVar1 >> 9) << 0x18;
    local_9c = 0x7f;
    *(uint **)(DAT_00008e08 + 8) = &local_a0;
    *(undefined4 *)(iVar3 + 4) = DAT_00008e0c;
    iVar3 = ProcessStatusCode();
    if (iVar3 == 0) {
      uVar4 = Cy_SysLib_EnterCriticalSection();
      iVar3 = Cy_Flash_ClockBackup();
      if ((iVar3 == 0) && (iVar3 = Cy_Flash_ClockConfig(), iVar3 == 0)) {
        *(uint **)(DAT_00008e08 + 8) = &local_a0;
        if (DAT_00008e10 < param_1) {
          local_a0 = DAT_00008e14;
          *(undefined4 *)(DAT_00008e08 + 4) = DAT_00008e18;
          local_9c = uVar1;
        }
        else {
          local_a0 = DAT_00008e1c | uVar1 << 0x10;
          *(undefined4 *)(DAT_00008e08 + 4) = DAT_00008e20;
        }
        iVar2 = ProcessStatusCode();
        iVar3 = Cy_Flash_ClockRestore();
        if (iVar2 != 0) {
          iVar3 = iVar2;
        }
      }
      Cy_SysLib_ExitCriticalSection(uVar4);
    }
  }
  return iVar3;
}

