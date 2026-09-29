
void AncsGetAppAttribute(int param_1,int param_2)

{
  uint uVar1;
  byte bVar2;
  byte bVar3;
  undefined1 local_50;
  undefined1 auStack_4f [63];
  
  if (*(short *)(param_1 + 4) != 0) {
    local_50 = 1;
    bVar2 = 0;
    do {
      bVar3 = bVar2 + 1;
      uVar1 = (uint)bVar2;
      bVar2 = bVar3;
    } while (*(char *)(param_2 + uVar1) != '\0');
    if (bVar3 < 0x3f) {
      FUN_00439be4(auStack_4f,param_2,bVar3);
    }
    auStack_4f[bVar3] = 0;
    AttcWriteReq(*DAT_004bf6c0,*(undefined2 *)(param_1 + 4),bVar3 + 2,&local_50);
  }
  return;
}

