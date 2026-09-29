
int touch_sub_3f88(int param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  ushort uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int *piVar6;
  byte bVar7;
  int iVar8;
  
  piVar6 = (int *)(*(int *)(param_3 + 0xc) + param_1 * 0x90);
  iVar2 = *piVar6;
  uVar1 = *(ushort *)(iVar2 + 0xe);
  iVar3 = *(int *)(param_3 + 8);
  bVar7 = *(byte *)(iVar2 + 0x21) & 3;
  if (bVar7 == 2) {
    iVar8 = ((uint)*(ushort *)(iVar3 + 0x3e) + (uint)*(ushort *)(iVar3 + 0x42)) * (uint)(uVar1 >> 2)
    ;
  }
  else {
    iVar8 = ((uint)*(ushort *)(iVar3 + 0x40) + (uint)*(ushort *)(iVar3 + 0x44)) * (uint)(uVar1 >> 2)
    ;
  }
  iVar4 = (uint)*(byte *)(iVar3 + 0x4d) + (uint)*(ushort *)(iVar2 + 0x2c);
  iVar2 = iVar4 * (uint)uVar1 +
          iVar8 + (uint)*(byte *)(iVar3 + 0x53) +
                  (uint)*(ushort *)(iVar3 + 0x30) + (uint)*(ushort *)(iVar3 + 0x32);
  if (bVar7 == 2) {
    iVar2 = iVar2 * 2;
  }
  uVar5 = (uint)*(byte *)(piVar6 + 0x21);
  iVar2 = __aeabi_uidiv(uVar5 * iVar2,0x2e,iVar4,uVar5,param_4);
  return iVar2 * 5;
}

