# views.py
from django.http import JsonResponse, HttpResponse
from django.views import View
from .file_handler import FileHandler
from .models import EncryptedFile

class FileUploadView(View):
    def post(self, request, *args, **kwargs):
        # Handle file upload
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return JsonResponse({'error': 'No file uploaded'}, status=400)

        # Handle Encryption and Storage
        file_name = uploaded_file.name
        try:
            file_url, encryption_key = FileHandler.encrypt_and_store(uploaded_file, file_name)

            # Save metadata to the database
            EncryptedFile.objects.create(
                file_name=file_name,
                file_key=encryption_key,
                file_path=file_url
            )

            return JsonResponse({
                'message': 'File uploaded and encrypted successfully',
                'file_url': file_url
            })

        except Exception as e:
            return JsonResponse({'error': f"An error occurred during file upload: {str(e)}"}, status=500)

    def get(self, request, *args, **kwargs):
        # Handle file retrieval
        file_name = request.GET.get('file_name')

        if not file_name:
            return JsonResponse({'error': 'File name not provided'}, status=400)

        try:
            # Handle Retrieveal and decryption
            decrypted_data = FileHandler.retrieve_and_decrypt(file_name)

            # Return the decrypted file as an attachment
            response = HttpResponse(decrypted_data, content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response

        except FileNotFoundError as e:
            return JsonResponse({'error': str(e)}, status=404)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except RuntimeError as e:
            return JsonResponse({'error': str(e)}, status=500)
