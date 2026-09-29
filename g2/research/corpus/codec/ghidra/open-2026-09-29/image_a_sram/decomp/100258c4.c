
/* WARNING: Restarted to delay deadcode elimination for space: register */

undefined4 gx8002_timer_dispatch(undefined4 param_1,uint param_2)

{
  uint uVar1;
  uint uVar2;
  uint *puVar3;
  int iVar4;
  
  iVar4 = 0;
  puVar3 = puRam1002592c;
  do {
    uVar2 = param_2;
    if (puVar3[7] != 0) {
      uVar1 = gx8002_clock_time_us();
      uVar2 = param_2;
      if (puVar3[6] <= param_2) {
        if (puVar3[6] == param_2) {
          if (uVar1 < puVar3[5]) goto LAB_10025914;
        }
        (*(code *)(*puVar3 & 0xfffffffe))(puVar3[1]);
        puVar3[3] = uVar1;
        puVar3[4] = param_2;
        *(longlong *)(puVar3 + 5) = (longlong)(int)(puVar3[2] * 1000) + CONCAT44(param_2,uVar1);
        if (puVar3[8] == 0) {
          puVar3[7] = 0;
        }
      }
    }
LAB_10025914:
    iVar4 = iVar4 + 1;
    puVar3 = puVar3 + 9;
    param_2 = uVar2;
    if (iVar4 == 10) {
      uRam00000000 = uRam00000000 | 1;
      return 0;
    }
  } while( true );
}

