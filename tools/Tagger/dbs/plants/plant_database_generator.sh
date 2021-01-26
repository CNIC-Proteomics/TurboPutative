# Author: Rafael Barrero Rodríguez
# Date: 2021-01-21
# Description: Generate database with all plant compounds from PlantCyc

# Download all files from ftp
wget ftp://ftp.plantcyc.org/Pathways/Data_dumps/PMN13_July2018/compounds/*

for FILE in $(ls | grep -v -E "plant_database_generator.sh|files")
do
    mv "$FILE" files/
done

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

# Obtain plant compound synonyms 
python ../scripts/getAllSynonyms.py plant_pre_database.tsv
mv ../scripts/allSynonyms.tsv plant_pre2_database.tsv
cat <(echo -e "Name\tPlantCyc_ID") <(tail -n+2 plant_pre2_database.tsv) > plant_pre3_database.tsv
rm plant_pre2_database.tsv