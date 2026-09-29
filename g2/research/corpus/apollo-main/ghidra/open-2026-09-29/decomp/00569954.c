
undefined8 FUN_00569954(int *param_1,undefined4 param_2,uint param_3,undefined4 *param_4)

{
  undefined4 *puVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  undefined4 *puVar5;
  undefined4 local_30;
  uint local_2c;
  undefined4 *local_28;
  
  iVar4 = 6;
  local_30 = param_2;
  if ((((param_1 != (int *)0x0) && (iVar3 = *param_1, iVar3 != 0)) &&
      (*(int *)(iVar3 + 4) == DAT_00569a40)) &&
     (local_2c = param_3, local_28 = param_4, iVar4 = FUN_00567e52(iVar3,&local_28),
     puVar1 = local_28, iVar4 == 0)) {
    puVar5 = local_28 + 5;
    cVar2 = FUN_00567fb0(puVar5);
    if ((param_3 & 0xff) != 0) {
      if (cVar2 == '\0') {
        cVar2 = '\x01';
      }
      else {
        cVar2 = '\0';
      }
    }
    iVar4 = FUN_00569748(param_2,puVar5,0);
    if (iVar4 == 0) {
      FUN_005696d4(param_2,cVar2,&local_2c,&local_30);
      FT_Outline_Done(*puVar1,puVar5);
      iVar4 = FT_Outline_New(*puVar1,local_2c,local_30,puVar5);
      if (iVar4 == 0) {
        *(undefined2 *)((int)puVar1 + 0x16) = 0;
        *(undefined2 *)puVar5 = 0;
        FUN_00569716(param_2,cVar2,puVar5);
        if (((uint)param_4 & 0xff) != 0) {
          FUN_00567f88(*param_1);
        }
        *param_1 = (int)puVar1;
        goto LAB_005699d8;
      }
    }
    FUN_00567f88(puVar1);
    if (((uint)param_4 & 0xff) == 0) {
      *param_1 = 0;
    }
  }
LAB_005699d8:
  return CONCAT44(local_30,iVar4);
}

