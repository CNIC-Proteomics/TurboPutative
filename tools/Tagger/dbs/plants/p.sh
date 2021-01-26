# Build file with all compounds and ID
ALL_COMPOUNDS=""

for FILE in $(ls files)
do
    echo $FILE
    FILE_PATH="files/$FILE"
    FILE_COMPOUNDS="$(tail -n+2 <(grep -E "^CPD-[0-9]+" "$FILE_PATH" | cut -d$'\t' -f2))"
    FILE_ID="$(tail -n+2 <(grep -E "^CPD-[0-9]+" "$FILE_PATH" | cut -d$'\t' -f1))"
    ALL_COMPOUNDS="$(cat <(echo -e "$ALL_COMPOUNDS") <(paste <(echo -e "$FILE_COMPOUNDS") <(echo -e "$FILE_ID")))"
done

cat <(echo -e "Name\tPlantCyc_ID") <(sort <(echo -e "$ALL_COMPOUNDS") | sed /^[[:space:]]*$/d) | uniq > plant_pre_database.tsv