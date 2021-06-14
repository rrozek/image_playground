# PBS Image Converter  

## Environment variables

Environment variables can be passed directly or via .env file provided with the repo. 

For development/testing file provided is enough  
```dotenv
DJANGO_SECRET_KEY=6@5nz8)0n+62ey!_@*3+x3%di)5q56yvio*_oujsc(oi$2$y#3
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=*
```
For production It should more likely look like:  

```dotenv
DJANGO_SECRET_KEY=SomeRandomlyGeneratedString
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=domain_name_of_the_server
```

## Build

To build the dockerimage all we need to do is:  
```
cd app
docker build -t image_api .
```

## Run
This will create 'image_api' dockerimage. To run the http server, call:  
```
docker run --env-file .env -p 8000:8000 --rm image_api
```
so, breaking it down into parts:  
1. `--env-file .env` pass env file  
2. `-p 8000:8000` map container 8000 to host 8000 port    
3. `--rm` mark as remove on shutdown    
4. `image_api` imagename    

from this point you should be able to visit 127.0.0.1:8000 and start querying for data.  
There is simple testing app provided via swagger in `api/swagger` endpoint

## Using API

Basically API expects data in following format:
```json
{
    "source": "<base64 encoded uri>",
    "sha256": "<sha256 hexdigest to verify data integrity>",
    "output": "url|base64"
}
```
`source` is always base64 encoded uri  
`sha256` is hexdigest of imagefile for server-side integrity verification  
`output` is expected output format. Two options are supported currently:  
1. `url` API will return URL where result image can be accessed/downloaded  
2. `base64` API will return base64 encoded URI with resulting image data  

Response from API is in form:  
```json
{
    "result": "success",
    "error_code": 0,
    "msg": "",
    "data": {
        "result": "http://127.0.0.1:8000/media/2b14588d-1d91-4357-ae33-a9f76d2ef7da.png"
    }
}
```
If `error_code` == 0 then `msg` is empty. Otherwise, short error description is provided.  
  
## Example
Example payloads are provided in repo in `app/samples` directory (`png2tiff.json` and `tiff2png.json`)
