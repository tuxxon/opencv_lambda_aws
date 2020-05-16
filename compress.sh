ZIPFILE=allinone.zip
unzip cv2-python37.zip 
cp app.py python/lib/python3.7/site-packages/
cd python/lib/python3.7/site-packages/
zip -r9 ../../../../$ZIPFILE .
cd -
