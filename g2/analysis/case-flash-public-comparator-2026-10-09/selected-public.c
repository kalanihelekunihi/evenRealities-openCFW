#include <stdint.h>
#define __IO volatile
typedef struct
{
  __IO uint32_t ACR;          /*!< FLASH Access Control register,                     Address offset: 0x00 */
       uint32_t RESERVED1;    /*!< Reserved1,                                         Address offset: 0x04 */
  __IO uint32_t KEYR;         /*!< FLASH Key register,                                Address offset: 0x08 */
  __IO uint32_t OPTKEYR;      /*!< FLASH Option Key register,                         Address offset: 0x0C */
  __IO uint32_t SR;           /*!< FLASH Status register,                             Address offset: 0x10 */
  __IO uint32_t CR;           /*!< FLASH Control register,                            Address offset: 0x14 */
  __IO uint32_t ECCR;          /*!< FLASH ECC bank 1 register,                        Address offset: 0x18 */
  __IO uint32_t ECC2R;         /*!< FLASH ECC bank 2 register,                        Address offset: 0x1C */
  __IO uint32_t OPTR;         /*!< FLASH Option register,                             Address offset: 0x20 */
  __IO uint32_t PCROP1ASR;    /*!< FLASH Bank PCROP area A Start address register,    Address offset: 0x24 */
  __IO uint32_t PCROP1AER;    /*!< FLASH Bank PCROP area A End address register,      Address offset: 0x28 */
  __IO uint32_t WRP1AR;       /*!< FLASH Bank WRP area A address register,            Address offset: 0x2C */
  __IO uint32_t WRP1BR;       /*!< FLASH Bank WRP area B address register,            Address offset: 0x30 */
  __IO uint32_t PCROP1BSR;    /*!< FLASH Bank PCROP area B Start address register,    Address offset: 0x34 */
  __IO uint32_t PCROP1BER;    /*!< FLASH Bank PCROP area B End address register,      Address offset: 0x38 */
       uint32_t RESERVED5[2]; /*!< Reserved5,                                         Address offset: 0x3C--0x40 */
  __IO uint32_t PCROP2ASR;    /*!< FLASH Bank2 PCROP area A Start address register,   Address offset: 0x44 */
  __IO uint32_t PCROP2AER;    /*!< FLASH Bank2 PCROP area A End address register,     Address offset: 0x48 */
  __IO uint32_t WRP2AR;       /*!< FLASH Bank2 WRP area A address register,           Address offset: 0x4C */
  __IO uint32_t WRP2BR;       /*!< FLASH Bank2 WRP area B address register,           Address offset: 0x50 */
  __IO uint32_t PCROP2BSR;    /*!< FLASH Bank2 PCROP area B Start address register,   Address offset: 0x54 */
  __IO uint32_t PCROP2BER;    /*!< FLASH Bank2 PCROP area B End address register,     Address offset: 0x58 */
       uint32_t RESERVED7[9]; /*!< Reserved7,                                         Address offset: 0x5C--0x7C */
  __IO uint32_t SECR;         /*!< FLASH security register ,                          Address offset: 0x80 */
} FLASH_TypeDef;
typedef enum
{
  HAL_OK       = 0x00U,
  HAL_ERROR    = 0x01U,
  HAL_BUSY     = 0x02U,
  HAL_TIMEOUT  = 0x03U
} HAL_StatusTypeDef;
#define FLASH_KEY1                      0x45670123U
#define FLASH_KEY2                      0xCDEF89ABU
#define FLASH_OPTKEY1                   0x08192A3BU
#define FLASH_OPTKEY2                   0x4C5D6E7FU
#define FLASH_CR_OPTLOCK_Pos                   (30U)
#define FLASH_CR_OPTLOCK_Msk                   (0x1UL << FLASH_CR_OPTLOCK_Pos)
#define FLASH_CR_OPTLOCK                       FLASH_CR_OPTLOCK_Msk
#define FLASH_CR_LOCK_Pos                      (31U)
#define FLASH_CR_LOCK_Msk                      (0x1UL << FLASH_CR_LOCK_Pos)
#define FLASH_CR_LOCK                          FLASH_CR_LOCK_Msk
#define READ_BIT(REG, BIT)    ((REG) & (BIT))
#define WRITE_REG(REG, VAL)   ((REG) = (VAL))
#define FLASH ((FLASH_TypeDef *)0x40022000UL)
HAL_StatusTypeDef HAL_FLASH_Unlock(void)
{
  HAL_StatusTypeDef status = HAL_OK;

  if (READ_BIT(FLASH->CR, FLASH_CR_LOCK) != 0x00U)
  {
    /* Authorize the FLASH Registers access */
    WRITE_REG(FLASH->KEYR, FLASH_KEY1);
    WRITE_REG(FLASH->KEYR, FLASH_KEY2);

    /* verify Flash is unlock */
    if (READ_BIT(FLASH->CR, FLASH_CR_LOCK) != 0x00U)
    {
      status = HAL_ERROR;
    }
  }

  return status;
}
HAL_StatusTypeDef HAL_FLASH_OB_Unlock(void)
{
  HAL_StatusTypeDef status = HAL_ERROR;

  if (READ_BIT(FLASH->CR, FLASH_CR_OPTLOCK) != 0x00U)
  {
    /* Authorizes the Option Byte register programming */
    WRITE_REG(FLASH->OPTKEYR, FLASH_OPTKEY1);
    WRITE_REG(FLASH->OPTKEYR, FLASH_OPTKEY2);

    /* verify option bytes are unlocked */
    if (READ_BIT(FLASH->CR, FLASH_CR_OPTLOCK) == 0x00U)
    {
      status = HAL_OK;
    }
  }

  return status;
}
