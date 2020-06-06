
import boto3
import botocore
import cv2
import json
import logging
import numpy
import os


def lambda_handler(event, context):

    print("==== event ===> {}".format(event))

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info('event parameter: {}'.format(event))

    src_filename = event['name']
    filename_set = os.path.splitext(src_filename)
    basename = filename_set[0]
    ext = filename_set[1]

    down_filename='/tmp/my_image{}'.format(ext)
    down_filename_gray='/tmp/my_image_gray{}'.format(ext)
    down_filename_ep='/tmp/my_image_ep{}'.format(ext)
    down_filename_de='/tmp/my_image_de{}'.format(ext)
    down_filename_style='/tmp/my_image_style{}'.format(ext)
    down_filename_ps_gray='/tmp/my_image_ps_gray{}'.format(ext)
    down_filename_ps_color='/tmp/my_image_ps_color{}'.format(ext)

    gray_filename='public/{}-gray{}'.format(basename,ext)
    ep_filename='public/{}-ep{}'.format(basename,ext)
    de_filename='public/{}-de{}'.format(basename,ext)
    style_filename='public/{}-style{}'.format(basename,ext)
    ps_gray_filename='public/{}-ps-gray{}'.format(basename,ext)
    ps_color_filename='public/{}-ps-color{}'.format(basename,ext)

    s3 = boto3.resource('s3')
    BUCKET_NAME = os.environ.get("BUCKET_NAME")
    S3_KEY = src_filename

    try:
        s3.Bucket(BUCKET_NAME).download_file(S3_KEY, down_filename)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist: s3://" + BUCKET_NAME + S3_KEY)
        else:
            raise

    image_src = cv2.imread(down_filename) 
    image_gray = cv2.cvtColor(image_src, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(down_filename_gray, image_gray) 

    image_ep = cv2.edgePreservingFilter(image_src, flags=1, sigma_s=60, sigma_r=0.4)
    cv2.imwrite(down_filename_ep, image_ep)

    image_de  = cv2.detailEnhance(image_src, sigma_s=10, sigma_r=0.15)
    cv2.imwrite(down_filename_de, image_de)

    image_stylization = cv2.stylization(image_src, sigma_s=60, sigma_r=0.45)
    cv2.imwrite(down_filename_style, image_stylization)

    image_ps_gray, image_ps_color = cv2.pencilSketch(image_src, sigma_s=60, sigma_r=0.07, shade_factor=0.05)
    cv2.imwrite(down_filename_ps_gray, image_ps_gray)
    cv2.imwrite(down_filename_ps_color, image_ps_color)

    s3 = boto3.client('s3')
    s3.upload_file(down_filename_gray, BUCKET_NAME, gray_filename)
    s3.upload_file(down_filename_ep, BUCKET_NAME, ep_filename)
    s3.upload_file(down_filename_de, BUCKET_NAME, de_filename)
    s3.upload_file(down_filename_style, BUCKET_NAME, style_filename)
    s3.upload_file(down_filename_ps_gray, BUCKET_NAME, ps_gray_filename)
    s3.upload_file(down_filename_ps_color, BUCKET_NAME, ps_color_filename)

    images = {
        "gray" : "https://{bucketName}.s3.ap-northeast-2.amazonaws.com/{grayName}".format(
            bucketName = BUCKET_NAME,
            grayName = gray_filename
        ),
        "edgePreserving" : "https://{bucketName}.s3.ap-northeast-2.amazonaws.com/{epName}".format(
            bucketName = BUCKET_NAME,
            epName = ep_filename
        ),
        "detailEnhance" : "https://{bucketName}.s3.ap-northeast-2.amazonaws.com/{deName}".format(
            bucketName = BUCKET_NAME,
            deName = de_filename
        ),
        "stylization" : "https://{bucketName}.s3.ap-northeast-2.amazonaws.com/{styleName}".format(
            bucketName = BUCKET_NAME,
            styleName = style_filename
        ),
        "pencilSketch_gray" : "https://{bucketName}.s3.ap-northeast-2.amazonaws.com/{psGrayName}".format(
            bucketName = BUCKET_NAME,
            psGrayName = ps_gray_filename
        ),
        "pencilSketch_color" : "https://{bucketName}.s3.ap-northeast-2.amazonaws.com/{psColorName}".format(
            bucketName = BUCKET_NAME,
            psColorName = ps_color_filename
        )
    }

    return {
        "statusCode": 200,
        "body": {
            "images": images
        },
    }

