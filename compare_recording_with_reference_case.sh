#!/bin/bash

echo "Path to Servirtium markdown from compatibility suite invocation (arg1): $1"

echo "cat $1 | " > .compatibility_suite_mock_replacements.sh

## GUIDs to neutralize

cat "$1" | grep -Ewo '[[:xdigit:]]{8}(-[[:xdigit:]]{4}){3}-[[:xdigit:]]{12}' | awk '!x[$0]++' | nl -n ln | awk ' { t = $1; $1 = $2; $2 = t; print; } ' | sed 's# #/REPLACED_UUID_FOR_COMPATIBILITY_TEST_#' | sed -e 's#$#/g" |#' | sed -e 's#^#sed "s/#' >> .compatibility_suite_mock_replacements.sh

## GUIDs to neutralize

cat "$1" | grep "date: " | cut -d":" -f2,3,4 | sed 's/^ *//g' | strptime -i '%a, %d %b %Y %H:%M:%S %Z' -f '%Y-%m-%d-%H:%M:%S-%Z @ %a,~%d~%b~%Y~%H:%M:%S~%Z%n' | sort | uniq | cut -d"@" -f2 | sed "s/UTC/GMT/" | sed "s/ /@/g" | nl -n ln | awk ' { t = $1; $1 = $2; $2 = t; print; } ' | sed "s/@/ /g" | sed "s/^ //" | sed 's# #/REPLACED_DATETIME_FOR_COMPATIBILITY_TEST_#' | sed -e 's#$#/g" |#' | sed -e 's#^#sed "s/#' | sed "s/~/ /g" >> .compatibility_suite_mock_replacements.sh

echo " cat > .compatibility_suite_normalized.md" >> .compatibility_suite_mock_replacements.sh

bash .compatibility_suite_mock_replacements.sh

# echo "See .compatibility_suite_normalized.md"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "DIR=${DIR}"

diffs=$(diff .compatibility_suite_normalized.md "${DIR}/compatibility_suite_reference.md")

# echo $foo

if [ -z "$diffs" ]
then
      echo "Servirtium reference recording (GUIDS and dates normalized) matches the contents of $1"
else
      diff .compatibility_suite_normalized.md "${DIR}/compatibility_suite_reference.md" > .compatibility_suite.diffs
      echo "Servirtium reference recording (${DIR}/compatibility_suite_reference.md; GUIDS and dates normalized) DOES NOT match the contents of $1"
      echo " see also .compatibility_suite_normalized.md"
      echo " see also .compatibility_suite.diffs"
fi