(define 
   (svg-clip-path 
       tifffilename 
       svgfilename 
       outputfilename
   )
   (let* 
       ( ;define vars
         (image (car (gimp-file-load RUN-NONINTERACTIVE tifffilename tifffilename)))
         (drawable (car (gimp-image-get-active-layer image)))
       )
     (gimp-vectors-import-from-file image svgfilename 1 1)
     (set! drawable (car (gimp-image-get-active-layer image)))                  
     (gimp-file-save RUN-NONINTERACTIVE image drawable outputfilename outputfilename)
     (gimp-image-delete image)
   )
)


