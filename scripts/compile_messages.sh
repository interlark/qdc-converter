#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
LOCALE_DIR="${SCRIPT_DIR}/../qdc_converter/data/locale"

find "${LOCALE_DIR}" -name \*.po -print -execdir sh -c 'msgfmt -f -o "$(basename "$0" .po).mo" "$0"' '{}' \;
