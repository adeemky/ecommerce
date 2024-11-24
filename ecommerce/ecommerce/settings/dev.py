from .base import *

DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.mysql',
       'NAME': env('DB_NAME'), # DB ADI
       'USER': env('DB_USER'),
       'PASSWORD': env('DB_PASSWORD'),
       'HOST': env('DB_HOST'), # localhost IP adresi
       'PORT': env('DB_PORT'), # MySQL'in varsayılan portu
   }
}

