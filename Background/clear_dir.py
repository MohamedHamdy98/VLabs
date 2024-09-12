import os
import shutil

def clear_directory(path):
    """
    Clears all files and subdirectories in the given directory path.

    Args:
    - path (str): Directory path to clear.

    Returns:
    - None
    """
    if os.path.exists(path):  # Ensure the path exists
        for file_name in os.listdir(path):
            file_path = os.path.join(path, file_name)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Remove the file or symbolic link
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Remove the directory and its contents
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
        print(f"Directory {path} cleared successfully.")
    else:
        print(f"Directory {path} does not exist.")



