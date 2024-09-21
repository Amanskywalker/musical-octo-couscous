# file_handler.py
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from cryptography.fernet import Fernet, InvalidToken
from .models import EncryptedFile
import os

class FileHandler:
    @staticmethod
    def encrypt_and_store(file, file_name):
        """Encrypt the file and store it in the file system."""
        # new encryption key
        encryption_key = Fernet.generate_key()
        cipher_suite = Fernet(encryption_key)

        # Encrypt
        encrypted_data = cipher_suite.encrypt(file.read())

        # Save
        file_path = FileHandler._upload_to_file_system(file_name, encrypted_data)

        return file_path, encryption_key.decode()

    @staticmethod
    def retrieve_and_decrypt(file_name):
        """Retrieve the file from the system and decrypt it."""
        try:
            # Fetch
            encrypted_file = EncryptedFile.objects.get(file_name=file_name)

            # Check if file exists
            if not default_storage.exists(encrypted_file.file_path):
                raise FileNotFoundError(f"File '{file_name}' not found on the storage system.")

            # Read the encrypted file
            with default_storage.open(encrypted_file.file_path, 'rb') as file:
                encrypted_data = file.read()

            # Decrypt the file
            cipher_suite = Fernet(encrypted_file.file_key.encode())
            decrypted_data = cipher_suite.decrypt(encrypted_data)

            return decrypted_data

        except EncryptedFile.DoesNotExist:
            raise FileNotFoundError(f"File '{file_name}' not found in the database.")
        except InvalidToken:
            raise ValueError("Decryption failed. Invalid encryption key or corrupted file.")
        except Exception as e:
            raise RuntimeError(f"An error occurred while retrieving the file: {str(e)}")

    @staticmethod
    def _upload_to_file_system(file_name, encrypted_data):
        """Save the encrypted data to the file system."""
        #TODO: this can be modified to store the data in S3 
        save_path = f'encrypted_files/{file_name}'
        file_path = default_storage.save(save_path, ContentFile(encrypted_data))
        return default_storage.url(file_path)
