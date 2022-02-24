#!/usr/bin/env bash
# MERCIER Wilfried - IRAP
# A bash wrapper to automatically add the filters in filter directory into Cigale database

for filter in $(find filters -type f);
do
   pcigale-filters add "$filter"
done

exit 0
