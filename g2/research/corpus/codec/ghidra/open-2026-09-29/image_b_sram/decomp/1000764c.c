
undefined4 FUN_1000764c(uint param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  byte bStack_19;
  
  iVar1 = DAT_1000778c;
  uVar3 = *(uint *)(DAT_1000778c + 4);
  if (param_1 < uVar3) {
    uVar4 = param_1 + param_2;
    param_1 = param_1 & 0xfffff000;
    uVar3 = ((uVar3 < uVar4) * uVar3 + (uVar3 >= uVar4) * uVar4) - param_1;
    if (uVar3 != 0) {
      iVar5 = DAT_1000778c + 0x11;
      do {
        if (uVar3 < 0x1000) {
          uVar3 = 0;
LAB_1000768c:
          do {
            FUN_10006c30(5,&bStack_19,1);
          } while ((bStack_19 & 1) != 0);
          FUN_10006cb0(6,bStack_19 & 1);
          uVar4 = (*(int *)(iVar1 + 8) + 0x1fffffff) * 8;
          *(char *)(iVar1 + 0x11) = (char)(param_1 >> (uVar4 & 0x3f));
          *(char *)(iVar1 + 0x12) = (char)(param_1 >> (uVar4 - 8 & 0x3f));
          *(char *)(iVar1 + 0x13) = (char)(param_1 >> (uVar4 - 0x10 & 0x3f));
          *(char *)(iVar1 + 0x14) = (char)(param_1 >> (uVar4 - 0x18 & 0x3f));
          FUN_10006cb0(0x20,iVar5,3);
          do {
            FUN_10006c30(5,&bStack_19,1);
          } while ((bStack_19 & 1) != 0);
          param_1 = param_1 + 0x1000;
        }
        else {
          if (((param_1 & 0x7fff) != 0) || (uVar3 < 0x10000)) {
            uVar3 = uVar3 - 0x1000;
            goto LAB_1000768c;
          }
          do {
            FUN_10006c30(5,&bStack_19,1);
          } while ((bStack_19 & 1) != 0);
          FUN_10006cb0(6,bStack_19 & 1);
          uVar4 = (*(int *)(iVar1 + 8) + 0x1fffffff) * 8;
          *(char *)(iVar1 + 0x11) = (char)(param_1 >> (uVar4 & 0x3f));
          *(char *)(iVar1 + 0x12) = (char)(param_1 >> (uVar4 - 8 & 0x3f));
          *(char *)(iVar1 + 0x13) = (char)(param_1 >> (uVar4 - 0x10 & 0x3f));
          *(char *)(iVar1 + 0x14) = (char)(param_1 >> (uVar4 - 0x18 & 0x3f));
          FUN_10006cb0(0xd8,iVar5,3);
          do {
            FUN_10006c30(5,&bStack_19,1);
          } while ((bStack_19 & 1) != 0);
        }
      } while (uVar3 != 0);
    }
    uVar2 = 0;
  }
  else {
    uVar2 = 0xffffffea;
  }
  return uVar2;
}

