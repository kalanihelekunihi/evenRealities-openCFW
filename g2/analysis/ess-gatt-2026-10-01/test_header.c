#include "ess_gatt.h"
#include <assert.h>
#include <string.h>
int main(void) {
 _Static_assert(G2_ESS_AUDIO_VALUE_BYTES+3==G2_ESS_AUDIO_ATT_BYTES,"ATT length");
 _Static_assert(G2_ESS_NOTIFY_HANDLE==0x864,"stock notification handle");
 assert(strlen(G2_ESS_SERVICE_UUID)==36);
 assert(strcmp(G2_ESS_NOTIFY_UUID,"00002760-08c2-11e1-9073-0e8ac72e6402")==0);
 return 0;
}
