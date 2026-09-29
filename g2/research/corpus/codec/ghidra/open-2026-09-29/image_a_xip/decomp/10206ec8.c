
undefined4 gx8002_context_acquire(uint param_1,int *param_2,undefined4 *param_3)

{
  int iVar1;
  int iVar2;
  
  iVar1 = (param_1 % 3) * 0x2140;
  iVar2 = iRam10206f04 + 0x80;
  *(int *)(iVar1 + iVar2) = iRam10206f04;
  *(int *)(iVar2 + iVar1 + 0x10) = iVar1 + 0x20 + iVar2;
  *param_2 = iVar2 + iVar1;
  *param_3 = 0x2140;
  return 0;
}

