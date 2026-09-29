
void FUN_005c5440(int param_1,int param_2,int param_3,uint param_4)

{
  undefined2 uVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  undefined4 local_b0;
  int local_ac;
  undefined4 local_a8;
  int local_a4;
  undefined1 auStack_a0 [16];
  undefined1 auStack_90 [16];
  undefined1 auStack_80 [16];
  int local_70;
  undefined4 local_64;
  int local_60;
  int local_58;
  uint uStack_1c;
  
  if (param_3 != 0xffff) {
    iVar4 = *(int *)(param_1 + 0x2c);
    uVar1 = *(undefined2 *)(iVar4 + 0x28);
    if ((param_4 & 0xffff) != (uint)*(ushort *)(iVar4 + 0x28)) {
      *(short *)(iVar4 + 0x28) = (short)param_4;
      *(ushort *)(iVar4 + 0x2a) = *(ushort *)(iVar4 + 0x2a) | 8;
    }
    uStack_1c = param_4;
    FUN_00489f5e(auStack_80);
    local_70 = param_2;
    FUN_00452988(iVar4,0x40000,auStack_80);
    local_58 = FUN_005c45e2(iVar4,0x40000);
    iVar3 = FUN_005c5722(param_1);
    if (iVar3 != 0) {
      local_ac = ((local_58 + *(int *)(local_60 + 0xc)) * param_3 + *(int *)(iVar3 + 0x18)) -
                 local_58 / 2;
      local_a4 = local_58 + *(int *)(local_60 + 0xc) + local_ac + -1;
      local_b0 = *(undefined4 *)(iVar4 + 0x14);
      local_a8 = *(undefined4 *)(iVar4 + 0x1c);
      cVar2 = FUN_00450bcc(auStack_90,param_2 + 0x18,&local_b0);
      if (cVar2 != '\0') {
        FUN_00439c04(auStack_a0,param_2 + 0x18,0x10);
        FUN_00439c04(param_2 + 0x18,auStack_90,0x10);
        local_64 = FUN_004997f8(iVar3);
        FUN_00489fe0(param_2,auStack_80,iVar3 + 0x14);
        FUN_00439c04(param_2 + 0x18,auStack_a0,0x10);
      }
      *(undefined2 *)(iVar4 + 0x28) = uVar1;
      *(ushort *)(iVar4 + 0x2a) = *(ushort *)(iVar4 + 0x2a) & 0xfff7;
    }
  }
  return;
}

