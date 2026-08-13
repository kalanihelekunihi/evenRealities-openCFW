#ifndef OPEN_CFW_TEST_NVDB_PRODUCT_MODE_HOST_H
#define OPEN_CFW_TEST_NVDB_PRODUCT_MODE_HOST_H
extern unsigned char open_cfw_test_nvdb_product_mode_record[4];
unsigned short open_cfw_test_nvdb_product_mode_crc(const unsigned char *, unsigned int, const unsigned short *);
int open_cfw_test_nvdb_product_mode_read(const char *, void *, unsigned short);
int open_cfw_test_nvdb_product_mode_write(const char *, const void *, unsigned short);
void open_cfw_test_nvdb_product_mode_diag(unsigned char);
void open_cfw_test_nvdb_product_mode_reset(void);
void open_cfw_test_nvdb_product_mode_set_stored(const unsigned char *, int);
#define OPEN_CFW_NVDB_PRODUCT_MODE_RECORD_ADDRESS ((unsigned long)&open_cfw_test_nvdb_product_mode_record[0])
#define OPEN_CFW_NVDB_PRODUCT_MODE_KEY "nvProdMode"
#define OPEN_CFW_NVDB_PRODUCT_MODE_CRC16(p,n,s) open_cfw_test_nvdb_product_mode_crc((p),(n),(s))
#define OPEN_CFW_NVDB_PRODUCT_MODE_READ(k,p,n) open_cfw_test_nvdb_product_mode_read((k),(p),(n))
#define OPEN_CFW_NVDB_PRODUCT_MODE_WRITE(k,p,n) open_cfw_test_nvdb_product_mode_write((k),(p),(n))
#define OPEN_CFW_NVDB_PRODUCT_MODE_DIAGNOSTIC(m) open_cfw_test_nvdb_product_mode_diag((m))
#endif
