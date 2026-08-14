#!/bin/sh
set -eu

if [ "$#" -ne 1 ]; then
    echo "usage: $0 /absolute/vendor-cache-directory" >&2
    exit 2
fi

vendor_dir=$1
case "$vendor_dir" in
    /*) ;;
    *) echo "vendor cache path must be absolute" >&2; exit 2 ;;
esac

sdk_name=nRF5_SDK_17.1.0_ddde560
sdk_url=https://developer.nordicsemi.com/nRF51_SDK/nRF5_SDK_v17.x.x/nRF5_SDK_17.1.0_ddde560.zip
sdk_sha=5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061
flashdb_name=FlashDB-4e5677408256f82d47cd56a6b04605dcee35ed9a
flashdb_url=https://github.com/armink/FlashDB/archive/4e5677408256f82d47cd56a6b04605dcee35ed9a.tar.gz
flashdb_sha=7758fb46976acebc754fb452bbac2144badc713a3e158bab8a8961bc112eca1b
bosch_name=BMA456_SensorAPI-3266db2c5de15be1a00232b8c0f2fd23e07934e0
bosch_url=https://github.com/boschsensortec/BMA456_SensorAPI/archive/3266db2c5de15be1a00232b8c0f2fd23e07934e0.tar.gz
bosch_sha=8c362c3bd107d0fdc480376788d18bccf908f46576530935cb25a58213491ffb
st_name=lis2dw12-pid-8d4bd522015004a9646102702901ba5a15ec6d39
st_url=https://github.com/STMicroelectronics/lis2dw12-pid/archive/8d4bd522015004a9646102702901ba5a15ec6d39.tar.gz
st_sha=cc12412b9363a371fe1eb161710c5dbe81d5b6e707f7e33187b41a722aa8f1f6
st25_name=fp-sns-stbox1-e9a35449b777699b5e1dd0f1466de0ead554893a
st25_url=https://github.com/STMicroelectronics/fp-sns-stbox1/archive/e9a35449b777699b5e1dd0f1466de0ead554893a.tar.gz
st25_sha=eecdc6795d5c949874d95739403aacaf6f0527c3fd476f7f78fda31e4d35faa6
tiny_aes_name=tiny-AES-c-e72b6eff0884673997d0ca6385169bbd9b31936d
tiny_aes_url=https://github.com/kokke/tiny-AES-c/archive/e72b6eff0884673997d0ca6385169bbd9b31936d.tar.gz
tiny_aes_sha=ed9099a1e25880eaaaba1da98ff2ff68b21498f0bf35b38ef0ebf7223448d265
iqs_name=flipperone-mcu-firmware-0a88e26bb8fd5b6afcdcc607fd748d7bc3d2b067
iqs_url=https://github.com/flipperdevices/flipperone-mcu-firmware/archive/0a88e26bb8fd5b6afcdcc607fd748d7bc3d2b067.tar.gz
iqs_sha=4a957ea082ae2146692567ece71abd0b122a6c7c914bc964cee64d3d68656199
azoteq_settings_name=zmk-driver-iqs7211e-436d3c42172abf812ec104521f29384fc02fc50e
azoteq_settings_url=https://github.com/sekigon-gonnoc/zmk-driver-iqs7211e/archive/436d3c42172abf812ec104521f29384fc02fc50e.tar.gz
azoteq_settings_sha=9398174dea8c219988745af246eefcd8b141ef974ac6dacff79784c5364ec967
goodix_democode_name=pebbleos-nonfree-2c0034a23b675a5f9a29e4a47e8b504c7a88e321
goodix_democode_url=https://github.com/coredevices/pebbleos-nonfree/archive/2c0034a23b675a5f9a29e4a47e8b504c7a88e321.tar.gz
goodix_democode_sha=48564d724f1de0004dd19ed3d8b156841400b7e652714f46dcb64d0397c76d29

mkdir -p "$vendor_dir"
stage=$(mktemp -d "${TMPDIR:-/tmp}/openr1-vendor.XXXXXX")
trap 'rm -rf "$stage"' EXIT HUP INT TERM

if [ ! -d "$vendor_dir/$sdk_name" ]; then
    curl --fail --location --silent --show-error "$sdk_url" -o "$stage/sdk.zip"
    printf '%s  %s\n' "$sdk_sha" "$stage/sdk.zip" | shasum -a 256 -c -
    unzip -q "$stage/sdk.zip" -d "$stage/sdk"
    mv "$stage/sdk/$sdk_name" "$vendor_dir/$sdk_name"
fi

if [ ! -d "$vendor_dir/$flashdb_name" ]; then
    curl --fail --location --silent --show-error "$flashdb_url" -o "$stage/flashdb.tar.gz"
    printf '%s  %s\n' "$flashdb_sha" "$stage/flashdb.tar.gz" | shasum -a 256 -c -
    tar -xzf "$stage/flashdb.tar.gz" -C "$stage"
    mv "$stage/$flashdb_name" "$vendor_dir/$flashdb_name"
fi

if [ ! -d "$vendor_dir/$bosch_name" ]; then
    curl --fail --location --silent --show-error "$bosch_url" -o "$stage/bosch.tar.gz"
    printf '%s  %s\n' "$bosch_sha" "$stage/bosch.tar.gz" | shasum -a 256 -c -
    tar -xzf "$stage/bosch.tar.gz" -C "$stage"
    mv "$stage/$bosch_name" "$vendor_dir/$bosch_name"
fi

if [ ! -d "$vendor_dir/$st_name" ]; then
    curl --fail --location --silent --show-error "$st_url" -o "$stage/st.tar.gz"
    printf '%s  %s\n' "$st_sha" "$stage/st.tar.gz" | shasum -a 256 -c -
    tar -xzf "$stage/st.tar.gz" -C "$stage"
    mv "$stage/$st_name" "$vendor_dir/$st_name"
fi

if [ ! -d "$vendor_dir/$st25_name" ]; then
    curl --fail --location --silent --show-error "$st25_url" -o "$stage/st25.tar.gz"
    printf '%s  %s\n' "$st25_sha" "$stage/st25.tar.gz" | shasum -a 256 -c -
    tar -xzf "$stage/st25.tar.gz" -C "$stage"
    mv "$stage/$st25_name" "$vendor_dir/$st25_name"
fi

if [ ! -d "$vendor_dir/$tiny_aes_name" ]; then
    curl --fail --location --silent --show-error "$tiny_aes_url" -o "$stage/tiny-aes.tar.gz"
    printf '%s  %s\n' "$tiny_aes_sha" "$stage/tiny-aes.tar.gz" | shasum -a 256 -c -
    tar -xzf "$stage/tiny-aes.tar.gz" -C "$stage"
    mv "$stage/$tiny_aes_name" "$vendor_dir/$tiny_aes_name"
fi

if [ ! -d "$vendor_dir/$iqs_name" ]; then
    curl --fail --location --silent --show-error "$iqs_url" -o "$stage/iqs7211e.tar.gz"
    printf '%s  %s\n' "$iqs_sha" "$stage/iqs7211e.tar.gz" | shasum -a 256 -c -
    tar -xzf "$stage/iqs7211e.tar.gz" -C "$stage"
    mv "$stage/$iqs_name" "$vendor_dir/$iqs_name"
fi

if [ ! -d "$vendor_dir/$azoteq_settings_name" ]; then
    curl --fail --location --silent --show-error "$azoteq_settings_url" -o "$stage/azoteq-settings.tar.gz"
    printf '%s  %s\n' "$azoteq_settings_sha" "$stage/azoteq-settings.tar.gz" | shasum -a 256 -c -
    tar -xzf "$stage/azoteq-settings.tar.gz" -C "$stage"
    mv "$stage/$azoteq_settings_name" "$vendor_dir/$azoteq_settings_name"
fi

if [ ! -d "$vendor_dir/$goodix_democode_name" ]; then
    curl --fail --location --silent --show-error "$goodix_democode_url" -o "$stage/goodix-democode.tar.gz"
    printf '%s  %s\n' "$goodix_democode_sha" "$stage/goodix-democode.tar.gz" | shasum -a 256 -c -
    tar -xzf "$stage/goodix-democode.tar.gz" -C "$stage"
    mv "$stage/$goodix_democode_name" "$vendor_dir/$goodix_democode_name"
fi

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python3 "$script_dir/verify_vendor.py" \
    --sdk-root "$vendor_dir/$sdk_name" \
    --flashdb-root "$vendor_dir/$flashdb_name" \
    --bma456-root "$vendor_dir/$bosch_name" \
    --lis2dw12-root "$vendor_dir/$st_name" \
    --st25dvxxkc-root "$vendor_dir/$st25_name/Drivers/BSP/Components/st25dvxxkc" \
    --tiny-aes-root "$vendor_dir/$tiny_aes_name" \
    --iqs7211e-root "$vendor_dir/$iqs_name" \
    --azoteq-settings-root "$vendor_dir/$azoteq_settings_name" \
    --goodix-democode-root "$vendor_dir/$goodix_democode_name/gh3x2x"
