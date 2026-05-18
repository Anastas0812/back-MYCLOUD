from rest_framework import serializers
from .models import File


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = [
            'id',
            'original_name',
            'size',
            'upload_date',
            'last_download',
            'comment',
            'special_link',
            'file_path',
        ]
        extra_kwargs = {
            'file_path': {'write_only': True}  #только запись без передачи фронтенду
        }
        read_only_fields = ['size', 'upload_date', 'last_download', 'special_link']
