import os

def count_python_lines_and_files(start_path="."):
    total_lines = 0
    total_files = 0

    for root, _, files in os.walk(start_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        line_count = sum(1 for line in lines if line.strip() != "")
                        total_lines += line_count
                        total_files += 1
                        print(f"{file_path}: {line_count} lines")
                except Exception as e:
                    print(f"Failed to read {file_path}: {e}")

    print("\n--- Summary ---")
    print(f"Total Python Files: {total_files}")
    print(f"Total Non-Empty Lines of Code: {total_lines}")

if __name__ == "__main__":
    count_python_lines_and_files()
