
## Deploying
`func azure functionapp publish AzureFileList`

## Use in Azure Data Factory

**Function Name**: `@concat('get_files?', '&storage_account=', pipeline().parameters.storage_account, '&container=', pipeline().parameters.container, '&folder=', pipeline().parameters.folder)`

**Function Key**: 
- Authentication: Anonymous
- Function Key: use default key from Function App Service