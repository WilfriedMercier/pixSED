#!/usr/bin/env bash
# MERCIER Wilfried - IRAP
# A bash wrapper to automatically add the filters in filter directory into Cigale database

for filter in $(ls filters);
do
   pcigale-filters add "$filter"
done

exit 0
