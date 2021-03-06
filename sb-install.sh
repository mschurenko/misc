#!/bin/bash

# search, install, update, redo slackbuilds pkgs

origin='git://slackbuilds.org/slackbuilds.git'
repo="$HOME/slackbuilds"
usage="\nusage: $0 [search|install|info|update|redo]\n"

chk_repo() {
	if [[ -d $repo ]];then
		cd $repo
	else
		echo "$repo doesn't exist"
		exit 4
	fi
}

dl_sb() {
	chk_repo
	if ! [[ -d $1 ]];then
		echo "$1 doesn't exist"
		exit 3
	fi	
	tmp=`mktemp -d`
	rsync -a $1/ $tmp
	cd $tmp
}

com=$1
pat=$2

case $com in
	search)
		chk_repo
		pkg=( `find . -type d ! -path './.git/*' -name "*$pat*"` )
		if [[ -z $pkg ]];then
			echo "$pat didin't match."
			exit 2
		fi
		for p in "${pkg[@]}";do
			echo $p
		done
	;;
	install)
		dl_sb $pat
		url=`awk -F= '/DOWNLOAD=/ {print $NF}' *.info | sed 's/"//g'`
		wget $url
		chmod +x ./*.SlackBuild
		output=`mktemp`
		sudo ./*.SlackBuild | tee $output
		sbpkg=`perl -lne 'print $1 if /^Slackware package (.*\.tgz)/' $output`
		sudo installpkg $sbpkg
		rm -rf $tmp
	;;
	info)
		dl_sb $pat
		cat README
		echo
		cat *.info
		rm -rf $tmp
	;;
	update)
		chk_repo
		git pull
	;;
	redo)
		cd
		rm -rf $repo
		git clone $origin
	;;
	*)
		echo -e $usage
esac
