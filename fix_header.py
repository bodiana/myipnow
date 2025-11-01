import os

# Root folder of your project
ROOT_DIR = r"C:\Users\Bodia\OneDrive\Робочий стіл\myipnow-main"

def delete_bak_files(root):
    count = 0
    for folder, _, files in os.walk(root):
        for file in files:
            if file.lower().endswith(".bak") or ".bak." in file.lower():
                file_path = os.path.join(folder, file)
                try:
                    os.remove(file_path)
                    print(f"🗑️ Deleted: {file_path}")
                    count += 1
                except Exception as e:
                    print(f"⚠️ Error deleting {file_path}: {e}")
    print(f"\n🎯 Done. {count} .bak file(s) removed from {root}.")

if __name__ == "__main__":
    delete_bak_files(ROOT_DIR)
