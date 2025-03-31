
## Deploying
`func azure functionapp publish AzureFileList`

## Use in Azure Data Factory

**Function Name**: 
```
@concat('get_files?',
'&con_env_in=', pipeline().parameters.con_env_in,
'&container=', pipeline().parameters.container,
'&folder=', pipeline().parameters.folder
)
```

**Function Key**: 
- Authentication: Anonymous
- Function Key: use default key from Function App Service