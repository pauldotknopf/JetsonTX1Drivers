#!/bin/bash

# Copyright (c) 2012-2014, NVIDIA CORPORATION.  All rights reserved.
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


#
# This script sync's NVIDIA's version of
# 1. the kernel source
# 2. the u-boot source
# from nv-tegra, NVIDIA's public git repository.
# The script also provides opportunities to the sync to a specific tag
# so that the binaries shipped with a release can be replicated.
#

# verify that git is installed
if  ! which git > /dev/null  ; then
  echo "ERROR: git is not installed. If your linux distro is 10.04 or later,"
  echo "git can be installed by 'sudo apt-get install git-core'."
  exit 1
fi

# source dir
LDK_DIR=$(cd `dirname $0` && pwd)
LDK_DIR="${LDK_DIR}/sources"
# script name
SCRIPT_NAME=`basename $0`
# info about sources
SOURCE_INFO="
k:kernel:nv-tegra.nvidia.com/linux-3.10.git:
u:u-boot:nv-tegra.nvidia.com/3rdparty/u-boot.git:
"
# exit on error on sync
EOE=0
# after processing SOURCE_INFO
NSOURCES=0
declare -a SOURCE_INFO_PROCESSED
# download all?
DALL=1

function Usages {
	local ScriptName=$1
	local LINE
	local OP
	local DESC

	echo "Use: $1 [options]"
	echo "Available general options are,"
	echo "     -h     :     help"
	echo "     -e     : exit on sync error"
	echo "     -d DIR : root of source is DIR"
	echo ""
	echo "By default, all sources are downloaded."
	echo "Only specified sources are downloaded, if one or more of the following options are mentioned."
	echo ""
	echo "$SOURCE_INFO" | while read LINE; do
		if [ ! -z "$LINE" ]; then
			OP=`echo "$LINE" | cut -f 1 -d ':'`
			DESC=`echo "$LINE" | cut -f 2 -d ':'`
			echo "     -${OP} [TAG]: Download $DESC source and optionally sync to TAG"
		fi
	done
	echo ""
}

function ProcessSwitch {
	local SWITCH="$1"
	local TAG="$2"
	local i

	for ((i=0; i < NSOURCES; i++)); do
		local OP=`echo "${SOURCE_INFO_PROCESSED[i]}" | cut -f 1 -d ':'`
		if [ "-${OP}" == "$SWITCH" ]; then
			SOURCE_INFO_PROCESSED[i]="${SOURCE_INFO_PROCESSED[i]}${TAG}:y"
			DALL=0
			return 0
		fi
	done

	echo "Terminating... wrong switch: ${SWITCH}" >&2
	Usages "$SCRIPT_NAME"
	exit 1
}

function DownloadAndSync {
	local WHAT_SOURCE="$1"
	local LDK_SOURCE_DIR="$2"
	local REPO_URL="$3"
	local TAG="$4"
	local RET=0

	if [ -d "${LDK_SOURCE_DIR}" ] ; then
		echo "Directory for $WHAT, ${LDK_SOURCE_DIR}, already exists!"
		pushd "${LDK_SOURCE_DIR}" > /dev/null
		git status 2>&1 >/dev/null
		if [ $? -ne 0 ]; then
			echo "But the directory is not a git repository -- clean it up first"
			echo ""
			echo ""
			popd > /dev/null
			return 1
		fi
		git fetch --all 2>&1 >/dev/null
		popd > /dev/null
	else
		echo "Downloading default $WHAT source..."

		git clone "$REPO_URL" -n ${LDK_SOURCE_DIR} 2>&1 >/dev/null
		if [ $? -ne 0 ]; then
			echo "$2 source sync failed!"
			echo ""
			echo ""
			return 1
		fi

		echo "The default $WHAT source is downloaded in: ${LDK_SOURCE_DIR}"
	fi

	if [ -z "$TAG" ]; then
		echo "Please enter a tag to sync $2 source to"
		echo -n "(enter nothing to skip): "
		read TAG
		TAG=`echo $TAG`
	fi

	if [ ! -z "$TAG" ]; then
		pushd ${LDK_SOURCE_DIR} > /dev/null
		git tag -l 2>/dev/null | grep -q -P "^$TAG\$"
		if [ $? -eq 0 ]; then
			echo "Syncing up with tag $TAG..."
			git checkout -b mybranch_$(date +%Y-%m-%d-%s) $TAG
			echo "$2 source sync'ed to tag $TAG successfully!"
		else
			echo "Couldn't find tag $TAG"
			echo "$2 source sync to tag $TAG failed!"
			RET=1
		fi
		popd > /dev/null
	fi
	echo ""
	echo ""

	return "$RET"
}

# prepare processing ....
GETOPT=":ehd:"

OIFS="$IFS"
IFS=$(echo -en "\n\b")
SOURCE_INFO_PROCESSED=($(echo "$SOURCE_INFO"))
IFS="$OIFS"
NSOURCES=${#SOURCE_INFO_PROCESSED[*]}

for ((i=0; i < NSOURCES; i++)); do
	OP=`echo "${SOURCE_INFO_PROCESSED[i]}" | cut -f 1 -d ':'`
	GETOPT="${GETOPT}${OP}:"
done

# parse the command line first
while getopts "$GETOPT" opt; do
	case $opt in
		d)
			case $OPTARG in
				-[A-Za-z]*)
					Usages "$SCRIPT_NAME"
					exit 1
					;;
				*)
					LDK_DIR="$OPTARG"
					;;
			esac
			;;
		e)
			EOE=1
			;;
		h)
			Usages "$SCRIPT_NAME"
			exit 1
			;;
		[A-Za-z])
			case $OPTARG in
				-[A-Za-z]*)
					eval arg=\$$((OPTIND-1))
					case $arg in
						-[A-Za-Z]-*)
							Usages "$SCRIPT_NAME"
							exit 1
							;;
						*)
							ProcessSwitch "-$opt" ""
							OPTIND=$((OPTIND-1))
							;;
					esac
					;;
				*)
					ProcessSwitch "-$opt" "$OPTARG"
					;;
			esac
			;;
		:)
			case $OPTARG in
				#required arguments
				d)
					Usages "$SCRIPT_NAME"
					exit 1
					;;
				#optional arguments
				[A-Za-z])
					ProcessSwitch "-$OPTARG" ""
					;;
			esac
			;;
		\?)
			echo "Terminating... wrong switch: $@" >&2
			Usages "$SCRIPT_NAME"
			exit 1
			;;
	esac
done
shift $((OPTIND-1))

GRET=0
for ((i=0; i < NSOURCES; i++)); do
	WHAT=`echo "${SOURCE_INFO_PROCESSED[i]}" | cut -f 2 -d ':'`
	REPO=`echo "${SOURCE_INFO_PROCESSED[i]}" | cut -f 3 -d ':'`
	TAG=`echo "${SOURCE_INFO_PROCESSED[i]}" | cut -f 4 -d ':'`
	DNLOAD=`echo "${SOURCE_INFO_PROCESSED[i]}" | cut -f 5 -d ':'`

	if [ $DALL -eq 1 -o "x${DNLOAD}" == "xy" ]; then
		DownloadAndSync "$WHAT" "${LDK_DIR}/${WHAT}_source" "git://${REPO}" "${TAG}"
		tRET=$?
		let GRET=GRET+tRET
		if [ $tRET -ne 0 -a $EOE -eq 1 ]; then
			exit $tRET
		fi
	fi
done

exit $GRET
