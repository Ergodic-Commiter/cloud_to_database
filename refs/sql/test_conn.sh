sqlcmd -S "fiserv-reports.database.windows.net" -d "fiserv-db" \
  --authentication-method ActiveDirectoryServicePrincipal \
  -U $AZURE_SP_CLIENT -P $AZURE_SP_PASS \
  -Q "SELECT DB_NAME() AS db, SUSER_SNAME() AS who;"