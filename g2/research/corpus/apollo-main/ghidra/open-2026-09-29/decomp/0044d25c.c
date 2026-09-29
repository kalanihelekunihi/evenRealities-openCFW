
void FUN_0044d25c(char param_1,int param_2,undefined4 param_3,undefined4 param_4,undefined4 param_5)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  undefined1 auStack_324 [256];
  undefined1 auStack_224 [512];
  
  if ((param_1 < '\x06') && ('\x01' < param_1)) {
    for (iVar2 = FUN_00454768(param_2); iVar2 != 0; iVar2 = iVar2 + -1) {
      if ((*(char *)(param_2 + iVar2) == '/') || (*(char *)(param_2 + iVar2) == '\\')) {
        iVar2 = iVar2 + 1;
        break;
      }
    }
    uVar3 = FUN_00473482();
    iVar1 = DAT_0044d320;
    if (*(int *)(DAT_0044d320 + 0x16c) != 0) {
      vsnprintf(auStack_324,0x100,param_5,&stack0x00000004);
      snprintf(auStack_224,0x200,DAT_0044d328,*(undefined4 *)(DAT_0044d324 + param_1 * 4),
               uVar3 / 1000,uVar3 % 1000,uVar3 - *(int *)(iVar1 + 0x170),param_4,auStack_324,
               param_2 + iVar2,param_3);
      (**(code **)(iVar1 + 0x16c))((int)param_1,auStack_224);
    }
    *(uint *)(iVar1 + 0x170) = uVar3;
  }
  return;
}

