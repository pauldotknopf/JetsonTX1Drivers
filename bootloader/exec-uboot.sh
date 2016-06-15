#!/bin/bash

# Copyright (c) 2015, NVIDIA CORPORATION.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#  * Neither the name of NVIDIA CORPORATION nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# exec-uboot.sh: Load U-Boot into RAM and execute it.
#	exec-uboot.sh performs the best in L4T release environment.
#
# Usage: Place the board in recovery mode and run:
#
#	exec-uboot.sh <target board>
#
#	for more detail enter 'exec-uboot.sh -h'

usage()
{
	cat << EOF
Usage: sudo ./exec-uboot.sh <target board> [<boot command>]
Where:
	target board: Valid target board name.
	boot command: Optional command to execute when U-Boot starts.
EOF

	exit 1
}

instance=
if [ $# -gt 1 -a "$1" == "--instance" ]; then
	instance="--instance $2"
	shift
	shift
fi

if [ $# -lt 1 -o $# -gt 2 ]; then
	usage
fi

board="$1"
bootcmd="$2"

LDK_DIR=$(cd `dirname $0`/.. && pwd)
LDK_DIR=`readlink -f "${LDK_DIR}"`
cd "${LDK_DIR}"

if [ ! -r "${board}.conf" ]; then
	echo "Error: Invalid target board - ${board}."
	usage
fi
source "${board}.conf"

flashapp=`basename "${FLASHAPP}"`
if [ "${flashapp}" != "tegraflash.py" ]; then
	echo $0 only works with tegraflash.py
	exit 1
fi

# Is fdtput in the PATH and executable?
hash fdtput
if [ $? -ne 0 ]; then
	echo "exec-uboot.sh required fdtput to be installed"
	echo "On Debian and derivatives, this is in the device-tree-compiler package"
	exit 1
fi

# If the user is not root, there is no point in going forward
if [ "${USER}" != "root" ]; then
	echo "exec-uboot.sh requires root privilege"
	exit 1
fi

BL_DIR="${LDK_DIR}/bootloader"
TARGET_DIR="${BL_DIR}/${target_board}"
KERNEL_DIR="${LDK_DIR}/kernel"
DTB_DIR="${KERNEL_DIR}/dtb"

tmp_dir="/tmp/exec-uboot.$$"
fn_img="${tmp_dir}/image.bin"
fn_addr="${tmp_dir}/load-addr.txt"

function rm_tmp_dir {
	rm -rf "${tmp_dir}"
}
trap rm_tmp_dir exit SIGHUP SIGINT SIGTERM

function chkerr {
	ret=$?
	if [ ${ret} -ne 0 ]; then
		echo $1
		exit ${ret}
	fi
}

mkdir -p "${tmp_dir}"
chkerr "Could not create temporary dir"

uboot_dir_orig="${TARGET_DIR}/${board}"
uboot_elf="${uboot_dir_orig}/u-boot"
uboot_binary_orig="${uboot_dir_orig}/u-boot.bin"
uboot_binary_dtb_orig="${uboot_dir_orig}/u-boot-dtb.bin"
uboot_dtb_orig="${uboot_dir_orig}/u-boot.dtb"

if [ -z "${bootcmd}" ]; then
	uboot_binary="${uboot_binary_dtb_orig}"
else
	uboot_binary_mod="${tmp_dir}/u-boot-dtb.bin.mod"
	uboot_dtb_mod="${tmp_dir}/u-boot.dtb.mod"

	cp "${uboot_dtb_orig}" "${uboot_dtb_mod}"
	chkerr "Temp DTB copy failed"

	fdtput -p -t x "${uboot_dtb_mod}" /config bootdelay 0xfffffffe
	chkerr "Temp DTB bootdelay set failed"

	fdtput -p -t s "${uboot_dtb_mod}" /config bootcmd "${bootcmd}"
	chkerr "Temp DTB bootcmd set failed"

	cat "${uboot_binary_orig}" "${uboot_dtb_mod}" > "${uboot_binary_mod}"
	chkerr "Temp U-Boot+DTB generation failed"

	uboot_binary="${uboot_binary_mod}"
fi

uboot_entry=`"${LDK_DIR}/elf-get-entry.py" "${uboot_elf}"`
chkerr "Could not determine entry point of bootloader binary"

"${BL_DIR}/gen-tboot-img.py" "${uboot_binary}" ${uboot_entry} \
	"${fn_img}" "${fn_addr}"
chkerr "Could not add TBOOT header to bootloader binary"

fake_pt="${tmp_dir}/fake-pt.xml"
cat > "${fake_pt}" <<ENDOFHERE
<?xml version="1.0"?>
<partition_layout version="01.00.0000">
    <device type="sdmmc" instance="3">
        <partition name="WB0" id="10" type="WB0">
            <allocation_policy> sequential </allocation_policy>
            <filesystem_type> basic </filesystem_type>
            <size> 6291456 </size>
            <file_system_attribute> 0 </file_system_attribute>
            <allocation_attribute> 8 </allocation_attribute>
            <percent_reserved> 0 </percent_reserved>
            <filename> ${TARGET_DIR}/warmboot.bin </filename>
        </partition>
    </device>
</partition_layout>
ENDOFHERE
chkerr "Could not create fake partition table file"

"${BL_DIR}/${flashapp}" \
	${instance} \
	--chip 0x21 \
	--cfg "${fake_pt}" \
	--applet "${LDK_DIR}/${SOSFILE}" \
	--bct "${TARGET_DIR}/BCT/${EMMC_BCT}" \
	--odmdata ${ODMDATA} \
	--boardconfig "${LDK_DIR}/${BCFFILE}" \
	--bldtb "${KERNEL_DIR}/dtb/${DTB_FILE}" \
	--kerneldtb "${KERNEL_DIR}/dtb/${DTB_FILE}" \
	--applet-cpu "${LDK_DIR}/${TBCFILE}" \
	--tos "${LDK_DIR}/${TOSFILE}" \
	--bl "${fn_img}" \
	--bl-load `cat "${fn_addr}"` \
	--wb "${TARGET_DIR}/warmboot.bin.encrypt" \
	--bpf "${LDK_DIR}/${BPFFILE}" \
	--cmd rcmbl
chkerr "Bootloader download failed"

# vi: ts=8 sw=8 noexpandtab
