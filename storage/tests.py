# tests.py
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from .models import EncryptedFile
import os

class FileUploadTests(TestCase):

    def test_file_upload_success(self):
        # Create a test file
        test_file = SimpleUploadedFile("test.txt", b"Hello World")

        # upload the file
        response = self.client.post(reverse('file-upload'), {'file': test_file})
        
        # Check the Response
        self.assertEqual(response.status_code, 200)
        self.assertIn('file_url', response.json())
        
        # Verify
        self.assertTrue(EncryptedFile.objects.filter(file_name="test.txt").exists())

    def test_file_upload_no_file(self):
        # request without file
        response = self.client.post(reverse('file-upload'))
        
        # Check for 400 status code
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertEqual(response.json()['error'], 'No file uploaded')

    def test_file_retrieve_success(self):
        # Upload a file
        test_file = SimpleUploadedFile("test.txt", b"Hello World")
        self.client.post(reverse('file-upload'), {'file': test_file})

        # Download the file
        response = self.client.get(reverse('file-upload'), {'file_name': 'test.txt'})
        
        # Check for the file content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"Hello World")
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="test.txt"')

    def test_file_retrieve_file_not_found_in_db(self):
        # Downloading the non existing file
        response = self.client.get(reverse('file-upload'), {'file_name': 'nonexistent.txt'})
        
        # Check for 404 (not found) status code
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json())
        self.assertEqual(response.json()['error'], "File 'nonexistent.txt' not found in the database.")

    def test_file_retrieve_file_not_found_in_storage(self):
        # Create a database entry for a file without uploading it to storage
        EncryptedFile.objects.create(file_name='test.txt', file_key='testkey', file_path='invalid_path.txt')

        # Try to download the file which is not present in storage
        response = self.client.get(reverse('file-upload'), {'file_name': 'test.txt'})
        
        # Check for 404 status code
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json())
        self.assertEqual(response.json()['error'], "File 'test.txt' not found on the storage system.")
    
    def test_file_retrieve_decryption_failure(self):
        # Upload a test file first
        test_file = SimpleUploadedFile("test.txt", b"Hello World")
        self.client.post(reverse('file-upload'), {'file': test_file})

        # Modify the database to create an invalid decryption key
        encrypted_file = EncryptedFile.objects.get(file_name="test.txt")
        encrypted_file.file_key = 'invalid_key'
        encrypted_file.save()

        # Check for decryption fail condition
        response = self.client.get(reverse('file-upload'), {'file_name': 'test.txt'})
        
        # Check for 400 (bad request) due to decryption failure
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertEqual(response.json()['error'], 'Decryption failed. Invalid encryption key or corrupted file.')
