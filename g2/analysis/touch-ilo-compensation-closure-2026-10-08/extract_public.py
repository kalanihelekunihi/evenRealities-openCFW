"""Selected pinned ILO source with explicit ARM32 register/global environment."""
from pathlib import Path
import argparse,re,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--pdl',type=Path,required=True);p.add_argument('--capsense',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();D=Path(__file__).resolve().parent;a.output.mkdir(parents=True,exist_ok=True)
prefix='''#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#define CY_IP_S8SRSSLT 1
#define CY_SYSCLK_SUCCESS 0u
#define CY_SYSCLK_BAD_PARAM 0x4a0001u
#define CY_SYSCLK_INVALID_STATE 0x4a0003u
#define CY_SYSCLK_STARTED 0x490004u
#define MAX_DELAY_US 2000000u
#define MIN_DELAY_US 100u
#define COEF_PHUNDRED 100u
#define ILO_PERIOD_PPH 2500u
#define SYS_CLK_DIVIDER 10u
#define ILO_FREQ_2MSB 40u
#define ILO_FREQ_3LSB 1000u
#define ILO_DESIRED_FREQ_HZ 40000u
#define CY_SYSLIB_DIV_ROUND(a,b) (((a)+(b)/2u)/(b))
#define REG(a) (*(volatile uint32_t *)(a))
#define SRSS_CLK_DFT_SELECT REG(0x40030034u)
#define SRSS_TST_DDFT_CTRL REG(0x40030018u)
#define SRSSLT_TST_TRIM_CNTR1 REG(0x4003001cu)
#define SRSSLT_TST_TRIM_CNTR2 REG(0x40030020u)
#define SRSS_CLK_DFT_SELECT_DFT_SEL1_Pos 8u
#define SRSS_CLK_DFT_SELECT_DFT_SEL1_Msk 0xf00u
#define SRSS_CLK_DFT_SELECT_DFT_SEL_ILO 1u
#define SRSS_CLK_DFT_SELECT_DFT_CHCK_MSK 0xf0fu
#define SRSS_CLK_DFT_SELECT_DFT_CHCK_VAL 0x100u
#define SRSS_TST_DDFT_CTRL_DFT_SEL0_Pos 0u
#define SRSS_TST_DDFT_CTRL_DFT_SEL0_Msk 0xfu
#define SRSS_TST_DDFT_CTRL_DFT_SEL1_Pos 8u
#define SRSS_TST_DDFT_CTRL_DFT_SEL1_Msk 0xf00u
#define SRSS_TST_DDFT_CTRL_DFT_SEL_Pos 0u
#define SRSS_TST_DDFT_CTRL_DFT_SEL_Msk 0xf0fu
#define SRSS_TST_DDFT_CTRL_DFT_SEL_CLK0 8u
#define SRSS_TST_DDFT_CTRL_DFT_SEL_CLK1 9u
#define SRSSLT_TST_TRIM_CNTR1_COUNTER_DONE_Msk 0x80000000u
#define _VAL2FLD(f,v) (((uint32_t)(v)<<f##_Pos)&f##_Msk)
#define CY_REG32_CLR_SET(r,f,v) ((r)=((r)&~f##_Msk)|_VAL2FLD(f,v))
typedef uint32_t cy_en_sysclk_status_t;
extern bool preventIloMeasurment,iloMeasurment;
extern uint32_t SystemCoreClock;
void Cy_SysClk_IloStartMeasurement(void);
void Cy_SysClk_IloStopMeasurement(void);
uint32_t Cy_SysClk_IloCompensate(uint32_t,uint32_t *);
typedef uint32_t cy_capsense_status_t;
#define CY_CAPSENSE_STATUS_BAD_PARAM 1u
#define CY_CAPSENSE_STATUS_SUCCESS 0u
#define CY_CAPSENSE_ILO_COMPENSATE_DELAY 500u
#define CY_CAPSENSE_ILO_FACTOR_SHIFT 24u
#define CY_CAPSENSE_1M_DIVIDER 1000000u
#define CY_CAPSENSE_ENABLE 1u
#define CY_CAPSENSE_LP_EN 1u
#define CY_CAPSENSE_MW_STATE_LP_WD_SCAN_MASK 0x20u
#define MSCLP_AOS_CTL_WAKEUP_TIMER_Msk 0xffffu
#define MSCLP_AOS_CTL_WAKEUP_TIMER_Pos 0u
typedef struct {volatile uint32_t pad[28];volatile uint32_t AOS_CTL;} MSCLP_Type;
typedef struct {MSCLP_Type *ptrHwBase;} channel_config;
typedef struct {uint8_t pad[8];channel_config *ptrChConfig;} common_config;
typedef struct {uint8_t pad[8];uint32_t status;} common_context;
typedef struct {uint8_t pad[28];uint32_t activeWakeupTimer,activeWakeupTimerCycles,wotScanInterval,wotScanIntervalCycles,iloCompensationFactor;} internal_context;
typedef struct {common_config *ptrCommonConfig;common_context *ptrCommonContext;internal_context *ptrInternalContext;} cy_stc_capsense_context_t;
_Static_assert(offsetof(MSCLP_Type,AOS_CTL)==0x70,"AOS offset");
_Static_assert(offsetof(common_config,ptrChConfig)==8,"channel offset");
_Static_assert(offsetof(common_context,status)==8,"status offset");
_Static_assert(offsetof(internal_context,iloCompensationFactor)==44,"factor offset");
_Static_assert(offsetof(cy_stc_capsense_context_t,ptrInternalContext)==8,"internal offset");
uint32_t Cy_CapSense_MsclpTimerCalcCycles(uint32_t,const cy_stc_capsense_context_t *);
''';bodies=[];receipts=[]
for path,names,pin in [(a.pdl,['Cy_SysClk_IloStartMeasurement','Cy_SysClk_IloStopMeasurement','Cy_SysClk_IloCompensate'],'35f1714623cfea682d5e285af80d50416b4c7bbc'),(a.capsense,['Cy_CapSense_IloCompensate'],'247a9a0f79eb976f144f5fbeb29488c1c2606517')]:
 s=path.read_text()
 for name in names:
  m=re.search(r'(?:void|cy_en_sysclk_status_t|cy_capsense_status_t)\s+'+name+r'\s*\([^;{]*\)\s*\{',s);i=m.end();depth=1
  while depth:
   if s[i]=='{':depth+=1
   if s[i]=='}':depth-=1
   i+=1
  bodies.append(s[m.start():i])
 receipts.append({'path':str(path),'pin':pin,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'functions':names})
c=a.output/'public-ilo.c';c.write_text(prefix+'\n'.join(bodies)+'\n');(D/'public-source-environment.json').write_text(json.dumps({'sources':receipts,'environment':prefix,'translation_unit_sha256':hashlib.sha256(c.read_bytes()).hexdigest(),'globals':'Static compRunStat BSS linked at20000f1c;preventIloMeasurment20000f1d,iloMeasurment20000f1e,SystemCoreClock20000878; public calculator peer boundstock5d71.','limits':['Verbatim selected bodies plus explicit type/macro/global environment, not full SDK build or unique producer.','Status values are fixed observed ARM32 environment, not a newly authenticated full core-lib header build.']},indent=2)+'\n');print(c)
