cd "C:\Users\jry\corona_data_dk"
"C:/PROGRA~1/R/R-36~1.2/bin/x64/Rscript.exe" data_extract_and_clean.R

git checkout master
git add .
git commit -m "daily update"
git push