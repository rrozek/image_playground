(define 
   (script-fu-import-svg-path-two 
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
     
(script-fu-register "script-fu-import-svg-path-two"
	"import svg path to tiff2"
	"import svg path to tiff2"
	"Jakub Rojek"
	"Jakub Rojek"
	"2020/04/20"
	"*"
	SF-STRING "tifffilename" "/home/jakub_rojek/repos/pbs/data/gimp_batch_test/easy.tiff"
	SF-STRING "svgfilename" "/home/jakub_rojek/repos/pbs/data/gimp_batch_test/easy.svg"
	SF-STRING "outputfilename" "/home/jakub_rojek/repos/pbs/data/gimp_batch_test/easy_tiff.tiff"
)
(script-fu-menu-register "script-fu-import-svg-path-two" "<Image>/Import/Paths")

