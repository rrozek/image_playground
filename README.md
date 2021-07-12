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
```
POST /api/png/tiff/?output=url HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: multipart/form-data; 
```

```bash
curl -X POST "http://127.0.0.1:8000/api/png/tiff/?output=url" -H  "accept: application/json" -H  "Content-Type: multipart/form-data" -H  "X-CSRFToken: QZE4jqhWqdiWyNZYYfoJx72G1o35HFlqYLeQfU3JMC8cEhEPlCH8F1ZC0oXLZahJ" -F "source=@174H_Cremeschminke_FACE_PAINT_HALLOWEEN_03.png;type=image/png"
```

accepted `output` values are: ['url', 'image']

in case of `url` request, 303 with Location is returned
```
HTTP/1.1 303 See Other
Location: http://127.0.0.1:8000/media/174H_Cremeschminke_FACE_PAINT_HALLOWEEN_03_by6tc5K.tiff
```

in case of `image` request, image is returned with content type valid for given API endpoint (image/png, image/tiff, image/postscript)
```
HTTP/1.1 200 OK
Content-Type: image/tiff
Content-Length: 42428190
```
